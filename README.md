# tesseract-ocr-lambda-function
AWS Lambda function that executes Tesseract OCR (*Optimal Character Recognition Engine*) on Base 64 encoded images.
<br><br>

### Dependencies
* [Python 3.6.8](https://www.python.org/downloads/release/python-368/)
    - Required for local testing.
* [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
    - Tesseract pre-compiled binaries for Linux and Windows are [included in this repo](https://github.com/sethepeterson/tesseract-ocr-lambda-function/tree/master/dependencies).
<br>

### Testing
Local testing is supported only for Windows systems. <br>
Modify [/test_suite](https://github.com/sethepeterson/tesseract-ocr-lambda-function/tree/master/test_suite) to add test cases. <br>
Execute [ocr_tester.py](https://github.com/sethepeterson/tesseract-ocr-lambda-function/tree/master/test_suite/ocr_tester.py) to run tests.
<br><br>

### Usage
Include a Base 64 encoded image in the function invocation payload. <br>
The function will return a JSON response with the following variables:
* text        -  String containing the recognized text or error info.
* statusCode  -  Integer representing function success status.

| Result  | Status Code |
| ------------- | ------------- |
| Success  | 200  |
| Invalid Base 64 | 400 |
| OCR error | 500 |
<br>

### Deployment
Use a Linux OS for step 1 and step 2 to avoid file permission errors within Lambda environments.
1. Recursively change project folder contents to permission number 755 (chmod).
2. Create ZIP file of project folder **contents** (not the project folder itself).
3. Sign up for an AWS account.
4. Create S3 bucket.
5. Upload ZIP file to S3 bucket.
6. Create Lambda function.
7. Configure Lambda function:
   
| Setting  | Value |
| ------------- | ------------- |
| Runtime  | Python 3.6  |
| Handler | lambda_handler.lambda_handler |
| Timeout | 30+ seconds |

8. Import code from S3 bucket.
9. Ready to use!
