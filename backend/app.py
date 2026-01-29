from flask import Flask, request, jsonify, render_template
import cv2
import easyocr
import re
import numpy as np
from PIL import Image
import io

app = Flask(__name__, template_folder='templates')

reader = easyocr.Reader(['en'], gpu=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Convert file to OpenCV image
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)
    data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    
    # OCR detection
    text1 = reader.readtext(img)
    
    # Clean text
    texts = []
    for bbox, text, score in text1:
        if score > 0.4:
            texts.append(text.strip())
    full_text = ' '.join(texts).upper()
    
    # Extract info
    dob_match = re.search(r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{1,2}\s+\d{4}', full_text)
    dob = dob_match.group(0) if dob_match else "Not Found"

    id_match = re.search(r'(\d{3,}-\d{3,}-\d{3,}|\d{9,})', full_text)
    id_number = id_match.group(0) if id_match else "Not Found"

    last_name_match = re.search(r'APELYIDO/ LAST NAME\s+([A-Z\s]+?)(?=\sMGA PANGALAN/)', full_text)
    last_name = last_name_match.group(1).strip() if last_name_match else "Not Found"

    first_name_match = re.search(r'MGA PANGALAN/ GIVEN NAMES\s+([A-Z\s]+?)(?=\sGITNANG APELYIDO/)', full_text)
    first_name = first_name_match.group(1).strip() if first_name_match else "Not Found"

    middle_name_match = re.search(r'GITNANG APELYIDO/.*?Middle Name\s*([A-Z\s]+?)(?=\sPETSA NG)', full_text, flags = re.IGNORECASE)
    middle_name = middle_name_match.group(1).strip() if middle_name_match else "Not Found"

    address_match = re.search(r'TIRAHAN/ADDRESS\s+(.+)', full_text, flags=re.IGNORECASE)
    address = address_match.group(1).strip() if address_match else "Not Found"
    
    return jsonify({
        "Date of Birth": dob,
        "ID Number": id_number,
        "Last Name": last_name,
        "First Name": first_name,
        "Middle Name": middle_name,
        "Address": address
    })

if __name__ == "__main__":
    app.run(debug=True)
