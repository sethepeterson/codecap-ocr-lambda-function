import sys
sys.path.append(".")

from ocr import OCR
import base64
import os
import shutil


# Define constants.
test_files_path = os.getcwd() + os.path.join(os.path.sep, 'test_suite', 'test_files', '{}')
test_passed = '\n{} -> PASSED'
test_failed = '\n{} -> FAILED\nExpected:\n{}\nActual:\n{}'

# Initialize test cases.
# Test cases should be modeled as a tuple: (<file name>, <expected output text>)
test_cases = []
test_cases.append(('google.PNG', 'Google\n\n'))
test_cases.append(('python1.PNG', ''))


# Execute test cases.
print('\n')
for file_name, expected_text in test_cases:

    # Convert file to encoded Base64 string.
    file_path = test_files_path.format(file_name)
    with open(file_path, 'rb') as image_file:
        base_64_string = base64.b64encode(image_file.read())

        # Create OCR object.
        ocr = OCR(debug_mode=True)

        # Create temp_files directory.
        os.makedirs(ocr.temp_files_directory_path, exist_ok=True)

        # Get output.
        (recognized_text, _) = ocr.parse_image(base_64_string=base_64_string)

        # Delete temp_files directory.
        shutil.rmtree(ocr.temp_files_directory_path)

        # Case: test passed.
        if recognized_text == expected_text:
            print(test_passed.format(file_name))

        # Case: test failed.
        else:
            print(test_failed.format(file_name, expected_text, recognized_text))
            
print('\n\n\n')
