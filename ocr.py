from pytesseract import pytesseract
from PIL import Image
from io import BytesIO
import base64
import os


class OCR:

    # Constants
    tesseract_exe_path = os.path.dirname(__file__) + '\\Tesseract-OCR\\tesseract'
    decoded_image_file_name = 'decoded_image.png'

    invalid_base_64_input = 'INVALID_BASE_64_INPUT'
    ocr_error = 'OCR_ERROR'
    no_text_detected = 'NO_TEXT_DETECTED'

    @staticmethod
    def parse_image(base_64_image: str) -> str:

        # Decode Base64 string to image.
        try:
            image = Image.open(BytesIO(base64.b64decode(base_64_image)))
        except:
            return OCR.invalid_base_64_input

        # Parse image.
        try:
            pytesseract.tesseract_cmd = OCR.tesseract_exe_path
            text = pytesseract.image_to_string(image)
        except:
            return OCR.ocr_error

        # Case: OCR recognized no text.
        if len(text) == 0:
            return OCR.no_text_detected

        # Return recognized text.
        return text
