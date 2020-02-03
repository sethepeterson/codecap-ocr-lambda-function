import base64
import os
import shutil
import subprocess


class OCR:

    # Tesseract paths
    tesseract_executable_relative_path = os.path.join('.', 'dependencies', 'Tesseract-OCR-Linux', 'tesseract')
    tesseract_lib_directory_path = os.getcwd() + os.path.join(os.path.sep, 'dependencies', 'Tesseract-OCR-Linux', 'lib')
    tesseract_data_parent_directory_path = os.getcwd() + os.path.join(os.path.sep, 'dependencies', 'Tesseract-OCR-Linux')

    # Temporary and output paths
    temp_files_directory_path = os.path.join(os.path.sep, 'tmp', 'temp_files')
    decoded_image_path = os.path.join(os.path.sep, 'tmp', 'temp_files', 'decoded_image.png')
    output_files_path = os.path.join(os.path.sep, 'tmp', 'temp_files', 'ocr_output')
    txt_output_file_path = os.path.join(os.path.sep, 'tmp', 'temp_files', 'ocr_output.txt')
    tsv_output_file_path = os.path.join(os.path.sep, 'tmp', 'temp_files', 'ocr_output.tsv')

    # Status codes and error messages
    success_status_code = 200
    invalid_base_64_string_status_code = 400
    ocr_error_status_code = 500

    # Decodes the Base 64 encoded image and executes Tesseract OCR.
    # Returns a tuple:
    #   1. OCR result
    #   2. Status code
    @staticmethod
    def parse_image(base_64_string: str, debug_mode: bool) -> (str, int):

        # Update paths if executing in a testing Windows environment.
        if (debug_mode):
            OCR.debug_mode_update_paths()

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
            command = 'LD_LIBRARY_PATH={} TESSDATA_PREFIX={} {} {} {}'.format(
                OCR.tesseract_lib_directory_path,
                OCR.tesseract_data_parent_directory_path,
                OCR.tesseract_executable_relative_path,
                OCR.decoded_image_path,
                OCR.output_files_path
            )
            # command = 'LD_LIBRARY_PATH={} TESSDATA_PREFIX={} ./tesseract {} {}'.format(
            #     os.path.join(os.getcwd(), 'lib'),
            #     os.getcwd(),
            #     '/tmp/imgres.png',
            #     '/tmp/result'
            # )
            
            # Update command if executing in a testing Windows environment.
            if (debug_mode):
                command = '{} {} {} txt tsv'.format(
                    OCR.tesseract_executable_relative_path,
                    OCR.decoded_image_path,
                    OCR.output_files_path
                )

            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
            shutil.rmtree(OCR.temp_files_directory_path)
            return (str(e), OCR.ocr_error_status_code)

        # Todo: at this point if OCR executed correctly there will be two output files:
        #   1. temp_files/ocr_output.txt    -   This will contain the recognized text in plaintext format.
        #   2. temp_files/ocr_output.tsv    -   This will contain the output in tab-serparated-value format.
        #                                       See: https://github.com/tesseract-ocr/tesseract/wiki/Command-Line-Usage
        #                                       I think this contains the data we can utilize to implement horizontal whitespacing.

        # Read output files.
        try:
            with open(OCR.txt_output_file_path, 'r') as txt_output_file:
                text = txt_output_file.read()
            shutil.rmtree(OCR.temp_files_directory_path)
        except Exception as e:
            shutil.rmtree(OCR.temp_files_directory_path)
            return (str(e), OCR.ocr_error_status_code)


        # Return recognized text.
        return (text, OCR.success_status_code)


    @staticmethod
    def debug_mode_update_paths():
        # Tesseract paths
        OCR.tesseract_executable_relative_path = os.getcwd() + os.path.join(os.path.sep, 'dependencies', 'Tesseract-OCR-Windows', 'tesseract')

        # Temporary and output paths
        OCR.temp_files_directory_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files')
        OCR.decoded_image_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files', 'decoded_image.png')
        OCR.output_files_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files', 'ocr_output')
        OCR.txt_output_file_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files', 'ocr_output.txt')
        OCR.tsv_output_file_path = os.getcwd() + os.path.join(os.path.sep, 'temp_files', 'ocr_output.tsv')
