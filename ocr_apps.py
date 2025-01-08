from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import keras_ocr
 
import cv2
import numpy as np
import re

app = FastAPI()

# Set up the Keras-OCR pipeline
pipeline = keras_ocr.pipeline.Pipeline()

def extract_info_from_id(image):
    """Extracts name and ID number from a Kenyan ID card image using Keras-OCR."""
    try:
        # Convert the OpenCV image (BGR) to RGB for Keras-OCR
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Perform OCR using Keras-OCR
        predictions = pipeline.recognize([rgb_image])[0]  # Process a single image

        # Combine the recognized text into a single string
        extracted_text = " ".join([text for text, _ in predictions])

        # Remove short words (less than 3 characters)
        extracted_text = re.sub(r'\b\w{1,2}\b', '', extracted_text).strip()

        # Patterns
        name_pattern = r"FULLNAMES\s+([A-Z]+\s[A-Z]+(?:\s[A-Z]+)?)\s+DATE"
        id_pattern = r"\b(\d{8})\b"  # Matches exactly 8 digits for Kenyan ID

        # Extract name
        name_match = re.search(name_pattern, extracted_text)
        name = name_match.group(1).strip() if name_match else "Name not found"

        # Extract ID number
        id_match = re.search(id_pattern, extracted_text)
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
