# tesseract-ocr-lambda-function
AWS Lambda function that executes Tesseract OCR on Base 64 encoded images.

### Dependencies
* Python 3.6.8 <br>
* Tesseract-OCR

### Testing
Local testing is supported for Linux and Windows systems. <br>
Modify ocr_tester.py to add test cases. <br>
Execute ocr_tester.py to run tests.

### Usage
Include a Base 64 encoded image to the function invocation payload. <br>
The function will return a JSON payload with the following variables:
* text        -  Will contain the recognized text or error info if applicable.
* statusCode  -  See below.


| Result  | Status Code |
| ------------- | ------------- |
| Success  | 200  |
| Invalid Base 64 | 400 |
| OCR error | 500 |
