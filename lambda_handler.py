import json
from ocr import OCR


# Executed when the Lambda function is called.
# Parameters:
#   base_64_string - string representing an image encoded using Base 64 format.
#   context        - N/A
def lambda_handler(base_64_string: str, context):
    (recognized_text, status_code) = OCR.parse_image(base_64_string=base_64_string)

    return {
        'text': json.dumps(recognized_text),
        'statusCode': json.dumps(status_code)
    }
