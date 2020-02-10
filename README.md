# tesseract-ocr-lambda-function
[![Python 3.7](https://img.shields.io/badge/python-3.7-green.svg)](https://www.python.org/downloads/release/python-375/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
<br>
AWS Lambda function that executes Tesseract OCR (*Optimal Character Recognition Engine*) on Base 64 encoded images.<br>
The function also implements horizontal whitespace detection through use of Tesseract's TSV output.
<br><br>

### Dependencies
* [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
    - Tesseract pre-compiled binaries for Amazon Linux 1 and Windows are [included in this repo](https://github.com/sethepeterson/tesseract-ocr-lambda-function/tree/master/dependencies).
* [Windows](https://www.microsoft.com/en-us/windows/get-windows-10)
    - Required for local testing.
* [Python 3.7.5](https://www.python.org/downloads/release/python-375/)
    - Required for local testing.
    - The Tesseract-OCR Linux binary in this repo is only compatible with Amazon Linux 1, which corresponds to Lambda Python runtimes ≤ Version 3.7.5. 
<br>

### Testing
Local testing is supported only for Windows 10 systems. <br>
Modify [/test_suite](https://github.com/sethepeterson/tesseract-ocr-lambda-function/tree/master/test_suite) to add test cases. <br>
Execute [ocr_tester.py](https://github.com/sethepeterson/tesseract-ocr-lambda-function/tree/master/test_suite/ocr_tester.py) to run tests.
<br><br>

### Usage
Include a Base 64 encoded image in the function invocation payload. <br>
The function will return a JSON response with the following variables:
* text        -  String containing the recognized text or error info.
* statusCode  -  Integer representing function success status. See table below:

| Result  | Status Code |
| ------------- | ------------- |
| Success  | 200  |
| Invalid Base 64 | 400 |
| OCR error | 500 |
<br>

### Deployment
1. Create a ZIP file with the following structure (tested using 7 Zip):
```bash
    .
    ├── lambda_handler.py
    ├── ocr.py
    └── dependencies
        └── tesseract_ocr_linux
```

2. Sign up for an AWS account.
3. Create S3 bucket.
4. Upload ZIP file to S3 bucket.
5. Create Lambda function.
6. Configure Lambda function with the following settings:
   
| Setting  | Value |
| ------------- | ------------- |
| Runtime  | Python 3.7  |
| Handler | lambda_handler.lambda_handler |
| Timeout | 30+ seconds |

7. Import source code from S3 bucket ZIP file.
8. Ready to use!
