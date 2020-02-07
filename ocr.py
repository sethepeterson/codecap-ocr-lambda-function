import base64
import os
import shutil
import subprocess
import csv

class OCR:

    # Tesseract paths
    tesseract_executable_path = os.getcwd() + os.path.join(os.path.sep, 'dependencies', 'Tesseract-OCR-Linux', 'tesseract')
    tesseract_lib_directory_path = os.getcwd() + os.path.join(os.path.sep, 'dependencies', 'Tesseract-OCR-Linux', 'lib')
    tesseract_data_parent_directory_path = os.getcwd() + os.path.join(os.path.sep, 'dependencies', 'Tesseract-OCR-Linux')

    # Temporary and output files paths
    # Note: tmp is the only editable directory within the Lambda environment.
    temp_files_directory_path = os.path.join(os.path.sep, 'tmp', 'temp_files')
    decoded_image_path = os.path.join(os.path.sep, 'tmp', 'temp_files', 'decoded_image.png')
    output_files_path = os.path.join(os.path.sep, 'tmp', 'temp_files', 'ocr_output')
    txt_output_file_path = os.path.join(os.path.sep, 'tmp', 'temp_files', 'ocr_output.txt')
    tsv_output_file_path = os.path.join(os.path.sep, 'tmp', 'temp_files', 'ocr_output.tsv')

    # Tesseract CLI command
    tesseract_cli_command = 'LD_LIBRARY_PATH={} TESSDATA_PREFIX={} {} {} {} txt tsv'

    # Status codes and error messages
    success_status_code = 200
    invalid_base_64_string_status_code = 400
    ocr_error_status_code = 500


    # Decodes the Base 64 encoded image and executes Tesseract OCR.
    # Returns a tuple:
    #   1. OCR result
    #   2. Status code
    @staticmethod
    def parse_image(base_64_string: str, debug_mode: bool = False) -> (str, int):

        # Update paths if executing in a testing Windows environment.
        if (debug_mode):
            OCR.debug_mode_update_variables()

        # Decode Base 64 string to image.
        try:
            os.makedirs(OCR.temp_files_directory_path, exist_ok=True)
            with open(OCR.decoded_image_path, 'wb') as decoded_image_file:
                decoded_image_file.write(base64.b64decode(base_64_string))
        except Exception as e:
            shutil.rmtree(OCR.temp_files_directory_path)
            return (str(e), OCR.invalid_base_64_string_status_code)

        # Execute OCR on decoded image.
        try:
            command = OCR.tesseract_cli_command.format(
                OCR.tesseract_lib_directory_path,
                OCR.tesseract_data_parent_directory_path,
                OCR.tesseract_executable_path,
                OCR.decoded_image_path,
                OCR.output_files_path
            )
            
            # Update command if executing in a Windows testing environment.
            if (debug_mode):
                command = OCR.tesseract_cli_command.format(
                    OCR.tesseract_executable_path,
                    OCR.decoded_image_path,
                    OCR.output_files_path
                )

            subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
            shutil.rmtree(OCR.temp_files_directory_path)
            return (str(e), OCR.ocr_error_status_code)

        # Todo: at this point if OCR executed correctly there will be two output files:
        #   1. temp_files/ocr_output.txt    -   This will contain the recognized text in plaintext format.
        #   2. temp_files/ocr_output.tsv    -   This will contain the output in tab-serparated-value format.
        #                                       See: https://github.com/tesseract-ocr/tesseract/wiki/Command-Line-Usage
        #                                       I think this contains the data we can utilize to implement horizontal whitespacing.

        # Read output files.


        # # Read the tsv file to detect indentations on new lines
        # lineNum = parNum = baseLine = 0
        # indents = []
        # with open(OCR.tsv_output_file_path) as tsvfile:
        #     reader = csv.reader(tsvfile, delimiter='\t')
        #     for row in reader:
        #         print(row)
        #         if (row[11].split()) and (row[0] != 'level') and ((int(row[4]) != lineNum) or (int(row[2]) != parNum)):
        #             if (baseLine == 0) or (baseLine > int(row[6])):
        #                 baseLine = int(row[6])
        #             lineNum = int(row[4])
        #             parNum = int(row[2])
        #             indents.append(' ' * round((int(row[6]) - baseLine)/16))

        # # Write indentations to the text output
        # try:
        #     with open(OCR.txt_output_file_path, 'r') as txt_output_file:
        #         text = ''
        #         count = 0
        #         line = txt_output_file.readline()

        #         while line:
        #             if count+1 > len(indents):
        #                 indents.append('')
        #             if line != '\n':
        #                 text += indents[count] + line
        #                 count += 1
        #             line = txt_output_file.readline()

        #     shutil.rmtree(OCR.temp_files_directory_path)
        # except Exception as e:
        #     shutil.rmtree(OCR.temp_files_directory_path)
        #     return (str(e), OCR.ocr_error_status_code)

        # Return recognized text.
        text = format_output()
        return (text, OCR.success_status_code)


    # This method is utilized to update path and command variables for Windows environment execution.
    @staticmethod
    def debug_mode_update_variables():

        # Tesseract path
        OCR.tesseract_executable_path = os.getcwd() + os.path.join(os.path.sep, 'dependencies', 'Tesseract-OCR-Windows', 'tesseract')

        # Temporary and output paths
        OCR.temp_files_directory_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files')
        OCR.decoded_image_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files', 'decoded_image.png')
        OCR.output_files_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files', 'ocr_output')
        OCR.txt_output_file_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files', 'ocr_output.txt')
        OCR.tsv_output_file_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files', 'ocr_output.tsv')

        # Tesseract CLI command
        # Note: Windows environment execution does not require LD_LIBRARY_PATH and TESSDATA_PREFIX specification.
        OCR.tesseract_cli_command = '{} {} {} txt tsv'


# Checks the TSV output for formatting errors & fixes them
# Returns a string containing the formatted output
def format_output() -> str:
    # Read the tsv file to detect indentations on new lines
    lineNum = parNum = baseLine = 0
    indents = []
    with open(OCR.tsv_output_file_path) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if (row[11].split()) and (row[0] != 'level') and ((int(row[4]) != lineNum) or (int(row[2]) != parNum)):
                if (baseLine == 0) or (baseLine > int(row[6])):
                    baseLine = int(row[6])
                lineNum = int(row[4])
                parNum = int(row[2])
                indents.append(' ' * round((int(row[6]) - baseLine)/16))

    # Write indentations to the text output
    with open(OCR.txt_output_file_path, 'r') as txt_output_file:
        text = ''
        count = 0
        line = txt_output_file.readline()

        while line:
            if count+1 > len(indents):
                indents.append('')
            if line != '\n':
                text += indents[count] + line
                count += 1
            line = txt_output_file.readline()
    return text.strip()