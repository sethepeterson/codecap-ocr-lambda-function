import base64
import binascii
import csv
import os
import shutil
import subprocess
import traceback
import ctypes

class OCR:

    ##############################################################################################################
    ##                                               Constants                                                  ##
    ##############################################################################################################

    def __init__(self, debug_mode: bool, aws_request_id: str = None):

        self.debug_mode = debug_mode

        # Status codes and error messages
        self.success_status_code = 200
        self.invalid_base_64_string_status_code = 400
        self.ocr_error_status_code = 500

        # Case: AWS Lambda environment execution.
        if not debug_mode:

            # Output files paths
            # Note: tmp is the only editable directory within Lambda environments.
            self.temp_files_directory_path = os.path.join(os.path.sep, 'tmp')
            self.output_files_prefix       = os.path.join(self.temp_files_directory_path, aws_request_id)
            self.png_output_file_path      = self.output_files_prefix + '.png'
            self.txt_output_file_path      = self.output_files_prefix + '.txt'
            self.tsv_output_file_path      = self.output_files_prefix + '.tsv'

            # Tesseract paths
            # Note: see OCR.give_tesseract_execution_permission for details.
            self.dependency_tesseract_directory_path  = os.path.join(os.getcwd(), 'dependencies', 'tesseract_ocr_linux')
            self.dependency_tesseract_path            = os.path.join(self.dependency_tesseract_directory_path, 'tesseract')
            self.executable_tesseract_path            = os.path.join(self.temp_files_directory_path, 'tesseract')
            self.tesseract_data_prefix_directory_path = os.path.join(self.dependency_tesseract_directory_path, 'tessdata')
            self.tesseract_lib_directory_path         = os.path.join(self.dependency_tesseract_directory_path, 'lib')
            

            # Tesseract CLI command
            self.tesseract_cli_command = 'LD_LIBRARY_PATH={} TESSDATA_PREFIX={} {} {} {} txt tsv'.format(
                self.tesseract_lib_directory_path,
                self.tesseract_data_prefix_directory_path,
                self.executable_tesseract_path,
                self.png_output_file_path,
                self.output_files_prefix
            )

        # Case: local Windows envrionment execution.
        else:

            # Temporary and output paths
            self.temp_files_directory_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files')
            self.output_files_prefix       = os.path.join(self.temp_files_directory_path, 'temp')
            self.png_output_file_path      = self.output_files_prefix + '.png'
            self.txt_output_file_path      = self.output_files_prefix + '.txt'
            self.tsv_output_file_path      = self.output_files_prefix + '.tsv'
            
            # Tesseract path
            self.tesseract_path = os.getcwd() + os.path.join(os.path.sep, 'dependencies', 'tesseract_ocr_windows', 'tesseract')

            # Tesseract CLI command
            # Note: Windows environment execution does not require LD_LIBRARY_PATH and TESSDATA_PREFIX specification.
            self.tesseract_cli_command = '{} {} {} txt tsv'.format(
                self.tesseract_path,
                self.png_output_file_path,
                self.output_files_prefix
            )


    ##############################################################################################################
    ##                                               Functions                                                  ##
    ##############################################################################################################

    # Decodes the Base 64 encoded image and executes Tesseract OCR.
    # Returns a tuple:
    #   1. OCR result
    #   2. Status code
    #   2. List< Tuple<recognized characters, confidence> >
    def parse_image(self, base_64_string: str) -> (str, int, [(str, int)]):
        # Decode Base 64 string to image.
        try:
            with open(self.png_output_file_path, 'wb') as png_output_file:
                png_output_file.write(base64.b64decode(base_64_string, validate=True))
        except (OSError, binascii.Error):
            return (traceback.format_exc(), self.invalid_base_64_string_status_code)

        # Give Tesseract execution permission if in a production environment and it has not been done.
        if not self.debug_mode and not os.path.isfile(self.executable_tesseract_path):
            self.give_tesseract_execution_permission()

        # Execute OCR on decoded image.
        try:
            subprocess.check_output(self.tesseract_cli_command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exception:
            error_text = traceback.format_exc() + '\n\nCommand output:\n' + str(exception.output)
            return (error_text, self.ocr_error_status_code)

        # Format recognized text.
        text = self.format_output()
        conf = self.get_confidence()

        # Delete temporary files.
        os.remove(self.png_output_file_path)
        os.remove(self.txt_output_file_path)
        os.remove(self.tsv_output_file_path)

        # Return recognized text.
        return (text, self.success_status_code, conf)


    # Checks the TSV output for formatting errors & fixes them
    # Returns a string containing the formatted output
    def format_output(self) -> str:

        # Read the tsv file to detect indentations on new lines
        lineNum = parNum = baseLine = 0
        indents = []
        with open(self.tsv_output_file_path) as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            for row in reader:
                if (row[11].split()) and (row[0] != 'level') and ((int(row[4]) != lineNum) or (int(row[2]) != parNum)):
                    if (baseLine == 0) or (baseLine > int(row[6])):
                        baseLine = int(row[6])
                    lineNum = int(row[4])
                    parNum = int(row[2])
                    indents.append(' ' * round((int(row[6]) - baseLine)/16))

        # Write indentations to the text output
        with open(self.txt_output_file_path, 'r') as txt_output_file:
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


    # Reads the TSV output file and constructs a list of recognized strings and their associated confidence value.
    def get_confidence(self) -> ctypes.Array:
        conf = []
        with open(self.tsv_output_file_path) as tsvfile:
           reader = csv.reader(tsvfile, delimiter='\t')
           list_iterator = iter(reader)
           next(list_iterator)
           for row in list_iterator:
               if row[11].split():
                   conf.append((row[11], row[10]))
        return conf


    # This method is utilized to create a Tesseract binary with executable permission.
    def give_tesseract_execution_permission(self):

        # Copy Tesseract binary to tmp directory.
        # Note: tmp is the only editable directory within Lambda environments.
        shutil.copyfile(self.dependency_tesseract_path,
                        self.executable_tesseract_path)

        # Change permissions to executable.
        os.chmod(self.executable_tesseract_path, 0o755)
