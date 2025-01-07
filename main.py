from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import pytesseract
import cv2
import numpy as np
import re
from io import BytesIO

app = FastAPI()

def extract_info_from_id(image):
    """Extracts name and ID number from a Kenyan ID card image."""
    try:
        # Preprocessing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # OCR with Tesseract
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,-'
        text = pytesseract.image_to_string(thresh, config=custom_config)
        print(text)
        # Remove short words (less than 3 characters)
        text = re.sub(r'\b\w{1,2}\b', '', text).strip()

        # Patterns
        name_pattern = r"FULLNAMES\s+([A-Z]+\s[A-Z]+(?:\s[A-Z]+)?)\s+DATE"
        id_pattern = r"\b(\d{8})\b"  # Matches exactly 8 digits for Kenyan ID

        # Extract name
        name_match = re.search(name_pattern, text)
        name = name_match.group(1).strip() if name_match else "Name not found"

        # Extract ID number
        id_match = re.search(id_pattern, text)
        id_number = id_match.group(1) if id_match else "ID not found"

        return name, id_number

    except Exception as e:
        return f"Error: {e}", None

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Read the image file
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Extract name and ID from the image
    name, id_number = extract_info_from_id(image)

    # Return the result in a JSON response
    return JSONResponse(content={"name": name, "id_number": id_number})
