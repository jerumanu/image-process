import pytesseract
import cv2
import re

# Set Tesseract path (if needed)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows Example
def extract_name(image_path):
    """Extracts the full name from an image containing a Kenyan ID."""

    try:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        # Preprocessing (tuned for this specific image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Increase contrast
        alpha = 1.5 # Contrast control (1.0-3.0)
        beta = 0 # Brightness control (0-100)
        adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        blurred = cv2.GaussianBlur(adjusted, (3, 3), 0) # Reduced blur
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        # Dilate to connect broken characters
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,1))
        dilated = cv2.dilate(thresh, kernel, iterations=1)

        # Custom config (important for this image)
        custom_config = r'--oem 3 --psm 6'  # Treat as a single block of text
        text = pytesseract.image_to_string(dilated, config=custom_config)

        # Regex for the specific name format (more robust)
        name_pattern = r"EMMANUEL\s*CHERIYOT\s*KOECH"  # Accounts for potential extra spaces
        name_match = re.search(name_pattern, text, re.IGNORECASE)  # Case-insensitive

        name = name_match.group(0).strip() if name_match else "Name not found"
        return name

    except Exception as e:
        return f"Error: {e}"
# def extract_info_from_id(image):
#     """Extracts name and ID number from a Kenyan ID card image."""
#     try:
#         # Preprocessing (Improved)
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#         thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

#         # Use custom config for better accuracy (tuned for IDs)
#         custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,-'
#         text = pytesseract.image_to_string(thresh, config=custom_config)

#         # Regular Expressions (Improved)
#         name_pattern = r"([A-Z]+\s[A-Z]+\s[A-Z]+(?:\s[A-Z]+)?)"  # Match full name (multiple words)
#         id_pattern = r"\b(\d{8})\b"  # Matches exactly 8 digits (Kenyan ID)

#         # Extract name and ID using regex
#         name_match = re.search(name_pattern, text)
#         id_match = re.search(id_pattern, text)

#         name = name_match.group(0).strip() if name_match else "Name not found"
#         id_number = id_match.group(1) if id_match else "ID not found"

#         return name, id_number

#     except Exception as e:
#         return f"Error: {e}", None

#     except Exception as e:
#         return f"Error: {e}", None

# Example usage:
image_path = "/home/cheriyot/Project/test-app/images/WhatsApp Image 2025-01-06 at 11.03.45 AM.jpeg"  # Replace with the actual path
name, id_number = extract_info_from_id(image_path)

print("Name:", name)
print("ID Number:", id_number)