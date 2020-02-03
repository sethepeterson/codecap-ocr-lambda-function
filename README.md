# tesseract-ocr-lambda-function
AWS Lambda function that executes Tesseract OCR on Base 64 encoded images.
<br><br>

### Dependencies
* Python 3.6.8 <br>
* Tesseract-OCR
<br>

### Testing
Local testing is supported for Linux and Windows systems. <br>
Modify ocr_tester.py to add test cases. <br>
Execute ocr_tester.py to run tests.
<br><br>

### Usage
Include a Base 64 encoded image in the function invocation payload. <br>
The function will return a JSON payload with the following variables:
* text        -  Will contain the recognized text or error info if applicable.
* statusCode  -  See below.

| Result  | Status Code |
| ------------- | ------------- |
| Success  | 200  |
| Invalid Base 64 | 400 |
| OCR error | 500 |
<br>

### Deployment
If you havn't modified any source code, skip to step 4.<br>
1. Use Linux OS for step 2 and step 3.
2. Recursively change project folder contents to permission number 755. (chmod)
3. Create ZIP file of project folder **contents** (not the project folder itself).
4. Sign up for AWS account.
5. Create S3 bucket.
6. Upload ZIP file to S3 bucket.
6. Create Lambda function.
7. Import code from S3 bucket.
8. Under settings, change timeout to 30 seconds.
9. Ready to use!
