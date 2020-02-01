from pytesseract import pytesseract
from PIL import Image
from io import BytesIO
import base64
import os


class OCR:

    # Paths
    tesseract_exe_path = os.path.dirname(__file__) + '\\Tesseract-OCR\\tesseract'

    # Status codes
    success_status_code = 200
    invalid_base_64_string_status_code = 400
    ocr_error_status_code = 500
    no_text_detected_status_code = 501

    # Decodes the Base 64 encoded image and executes Tesseract OCR.
    # Returns a tuple:
    #   1. OCR result
    #   2. Status code
    @staticmethod
    def parse_image(base_64_image: str) -> (str, int):

        # Decode Base 64 string to image.
        try:
            image = Image.open(BytesIO(base64.b64decode(base_64_image)))
        except:
            return (None, OCR.invalid_base_64_string_status_code)

        # Execute OCR on image.
        try:
            pytesseract.tesseract_cmd = OCR.tesseract_exe_path
            text = pytesseract.image_to_string(image)
        except:
            return (None, OCR.ocr_error_status_code)

        # Case: OCR recognized no text.
        if len(text) == 0:
            return (None, OCR.no_text_detected_status_code)

        # Return recognized text.
        return (text, OCR.success_status_code)
