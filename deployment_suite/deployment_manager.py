import os
import time
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from full_permission_zip_file import FullPermissionZipFile

import sys
from subprocess import Popen, PIPE

class DeploymentManager:

    def __init__(self):
        self.base_directory_path = os.getcwd()
        self.zip_file_path = os.path.join(self.base_directory_path, 'deployment_suite', 'tesseract-ocr-lambda-deployment-package.zip')

        self.lambda_handler_file_path = os.path.join(self.base_directory_path, 'lambda_handler.py')
        self.lambda_handler_file_path_output = 'lambda_handler.py'

        self.ocr_file_path = os.path.join(self.base_directory_path, 'ocr.py')
        self.ocr_file_path_output = 'ocr.py'

        self.tesseract_ocr_linux_directory_path = os.path.join(self.base_directory_path, 'dependencies', 'tesseract_ocr_linux')

        self.seven_zip_executable_path = os.path.join(self.base_directory_path, 'deployment_suite', '7z.exe')
        self.seven_zip_command = '{} a -tzip {} {}'


    def make_package(self):

        try:
            print('\nCreating deployment package...')
        
            with ZipFile(self.zip_file_path, 'w', compression=ZIP_DEFLATED) as zip_file:

                file_path_list = []

                # Tesseract-OCR Linux binary directory
                for directory_path, _, file_names in os.walk(self.tesseract_ocr_linux_directory_path):
                   for file_name in file_names:
                       file_path = os.path.join(directory_path, file_name)
                       output_path = os.path.relpath(file_path, self.base_directory_path)
                        self.archive_file(zip_file, file_path,
                                          output_path, encoding='Latin-1')
                

                self.archive_file(zip_file,
                                  os.path.join(self.base_directory_path, 'full_permission_zip_file.py'),
                                  'full_permission_zip_file.py',
                                  encoding='utf-8')
            
                # # lambda_handler.py and ocr.py
                # self.archive_file(zip_file,
                #                   self.lambda_handler_file_path,
                #                   self.lambda_handler_file_path_output,
                #                   encoding='utf-8')

                # self.archive_file(zip_file,
                #                   self.ocr_file_path,
                #                   self.ocr_file_path_output,
                #                   encoding='utf-8')

                       
            print('Deployment package created.\n')
        
        except Exception as e:
            print('Error creating deployment package:\n{}'.format(str(e)))


    # Writes the file to the ZIP file with Latin-1 encoding (needed for Tesseract binary).
    def archive_file(self, zip_file: ZipFile, file_path: str, file_output_path: str, encoding: str = None):
        zip_info = ZipInfo(file_output_path, date_time=time.localtime())
        zip_info.external_attr = 0o755 << 16
        # zip_info.external_attr = 0x81ed0000          # -rwxrwxrwx
        # zip_info.external_attr = 2180972544          # -rwxrwxrwx
        # zip_info.external_attr = 0000001          # -rwxrwxrwx

        with open(file_path, encoding=encoding) as file:
            zip_file.writestr(zip_info, file.read())


###################################################################################################################

# Create ZIP file deployment package.
DeploymentManager().make_package()
