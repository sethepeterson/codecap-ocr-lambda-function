import base64
import csv
import os
import shutil
import stat
import subprocess
import traceback


class OCR:
    
    # Output files paths
    # Note: tmp is the only editable directory within Lambda environments.
    temp_files_directory_path = os.path.join(os.path.sep, 'tmp', 'temp_files')
    decoded_image_path        = os.path.join(temp_files_directory_path, 'decoded_image.png')
    output_files_path         = os.path.join(temp_files_directory_path, 'ocr_output')
    txt_output_file_path      = os.path.join(temp_files_directory_path, 'ocr_output.txt')
    tsv_output_file_path      = os.path.join(temp_files_directory_path, 'ocr_output.tsv')

    # Tesseract paths
    # Note: see OCR.give_tesseract_execution_permission for details.
    dependency_tesseract_directory_path  = os.path.join(os.getcwd(), 'dependencies', 'tesseract_ocr_linux')
    executable_tesseract_directory_path  = os.path.join(temp_files_directory_path, 'tesseract_ocr_linux')
    tesseract_data_prefix_directory_path = os.path.join(temp_files_directory_path, 'tesseract_ocr_linux', 'tessdata')
    tesseract_lib_directory_path         = os.path.join(executable_tesseract_directory_path, 'lib')
    tesseract_path                       = os.path.join(executable_tesseract_directory_path, 'tesseract')

    # Tesseract CLI command
    tesseract_cli_command = 'LD_LIBRARY_PATH={} TESSDATA_PREFIX={} {} {} {} txt tsv'

    # Status codes and error messages
    success_status_code                = 200
    invalid_base_64_string_status_code = 400
    ocr_error_status_code              = 500


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
            os.makedirs(OCR.temp_files_directory_path)
            with open(OCR.decoded_image_path, 'wb') as decoded_image_file:
                decoded_image_file.write(base64.b64decode(base_64_string))
        except:
            return (traceback.format_exc(), OCR.invalid_base_64_string_status_code)

        # Execute OCR on decoded image.
        try:
            # Create CLI command depending on DEBUG_MODE.
            command = None
            if (debug_mode):
                command = OCR.tesseract_cli_command.format(
                    OCR.tesseract_path,
                    OCR.decoded_image_path,
                    OCR.output_files_path
                )
            else:
                OCR.give_tesseract_execution_permission()
                command = OCR.tesseract_cli_command.format(
                    OCR.tesseract_lib_directory_path,
                    OCR.tesseract_data_prefix_directory_path,
                    OCR.tesseract_path,
                    OCR.decoded_image_path,
                    OCR.output_files_path
                )
            
            # Execute CLI command.
            subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            # return (test, OCR.ocr_error_status_code)
        except subprocess.CalledProcessError as e:
            error_text = traceback.format_exc() + '\n\nCommand output:\n' + str(e.output)
            return (error_text, OCR.ocr_error_status_code)

        # Return recognized text.
        text = format_output()
        return (text, OCR.success_status_code)


    # This method is utilized to create a Tesseract binary with executable permission.
    @staticmethod
    def give_tesseract_execution_permission():
        # Copy Tesseract binary directory to tmp directory.
        # Note: tmp is the only editable directory within Lambda environments.
        shutil.copytree(OCR.dependency_tesseract_directory_path,
                        OCR.executable_tesseract_directory_path)

        # Change permissions to executable.
        for directory_path, _, file_names in os.walk(OCR.executable_tesseract_directory_path):
            for file_name in file_names:
                file_path = os.path.join(directory_path, file_name)
                os.chmod(file_path, 0o755)


    # This method is utilized to update path and command variables for Windows environment execution.
    @staticmethod
    def debug_mode_update_variables():

        # Tesseract path
        OCR.tesseract_path = os.getcwd() + os.path.join(os.path.sep, 'dependencies', 'tesseract_ocr_windows', 'tesseract')

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