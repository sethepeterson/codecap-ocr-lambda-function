import json
from ocr import OCR


# Executed when the Lambda function is called.
# Parameters:
#   base_64_string - string representing an image encoded using Base 64 format.
#   context        - contains AWS info.
def lambda_handler(base_64_string: str, context):
    ocr = OCR(debug_mode=False, aws_request_id=context.aws_request_id)
    (status_code, recognized_text, confidence_values) = ocr.parse_image(base_64_string=base_64_string)

    return {
        'statusCode': json.dumps(status_code),
        'recognizedText': json.dumps(recognized_text),
        'confidenceValues': json.dumps(confidence_values)
    }
