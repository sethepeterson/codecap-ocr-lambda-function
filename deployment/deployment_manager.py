import os
import time
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import sys
from subprocess import Popen, PIPE

class DeploymentManager:

    def __init__(self):
        self.base_directory_path = os.getcwd()
        self.zip_file_path = os.path.join(self.base_directory_path, 'deployment', 'tesseract-ocr-lambda-deployment-package.zip')

        self.lambda_handler_file_path = os.path.join(self.base_directory_path, 'lambda_handler.py')
        self.lambda_handler_file_path_output = 'lambda_handler.py'

        self.ocr_file_path = os.path.join(self.base_directory_path, 'ocr.py')
        self.ocr_file_path_output = 'ocr.py'

        self.tesseract_ocr_linux_directory_path = os.path.join(
        self.base_directory_path, 'dependencies', 'tesseract_ocr_linux')


    def make_package(self):

        try:
            print('\nCreating deployment package...')
        
            with ZipFile(self.zip_file_path, 'w', compression=ZIP_DEFLATED) as zip_file:
            
                # lambda_handler.py and ocr.py
                self.archive_file(zip_file,
                                  self.lambda_handler_file_path,
                                  self.lambda_handler_file_path_output)

                self.archive_file(zip_file,
                                  self.ocr_file_path,
                                  self.ocr_file_path_output)

                # Tesseract-OCR Linux binary directory
                for directory_path, _, file_names in os.walk(self.tesseract_ocr_linux_directory_path):
                   for file_name in file_names:
                        file_path = os.path.join(directory_path, file_name)
                        output_path = os.path.relpath(file_path, self.base_directory_path)
                        self.archive_file(zip_file, file_path, output_path)
                       
            print('Deployment package created.\n')
        
        except Exception as e:
            print('Error creating deployment package:\n{}'.format(str(e)))


    # Writes the file to the ZIP file with Latin-1 encoding (needed for Tesseract binary).
    def archive_file(self, zip_file: ZipFile, file_path: str, file_output_path: str):
        zip_info = ZipInfo(file_output_path, date_time=time.localtime())
        with open(file_path, encoding='Latin-1') as file:
            zip_file.writestr(zip_info, file.read())


###################################################################################################################

# Create ZIP file deployment package.
DeploymentManager().make_package()
