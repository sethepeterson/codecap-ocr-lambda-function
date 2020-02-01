import sys
sys.path.append(".")

from ocr import OCR
import base64
import os

class OCRTester:

    def __init__(self):
        # Constants
        self.test_files_path = os.path.dirname(__file__) + '\\test_files\\{}'
        self.test_passed = '\n{} -> PASSED'
        self.test_failed = '\n{} -> FAILED\nExpected:\n{}\nActual:\n{}'

        # Initialize test cases.
        # Test cases should be represented as a tuple: (<fileName>, <expected output text>)
        self.test_cases = []
        self.test_cases.append( ('google.PNG', 'Google') )
        self.test_cases.append( ('python1.PNG', ''))


    def start(self):
        print('\n')

        for test_case in self.test_cases:
            # Get file name and expected output.
            file_name = test_case[0]
            expected_text = test_case[1]

            # Convert file to encoded Base64 string.
            file_path = self.test_files_path.format(file_name)
            with open(file_path, 'rb') as image_file:
                base_64_string = base64.b64encode(image_file.read())

            # Get OCR output.
            (recognized_text, _) = OCR.parse_image(base_64_string)

            # Case: test passed.
            if recognized_text == expected_text:
                print(self.test_passed.format(file_name))

            # Case: test failed.
            else:                
                print(self.test_failed.format(file_name, expected_text, recognized_text))
        print('\n\n\n')


# Start testing.
OCRTester().start()
