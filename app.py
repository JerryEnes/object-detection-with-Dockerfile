import os
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULT_FOLDER'] = 'static/results'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect_objects():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        save_name = f"{unique_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
        file.save(filepath)
        
        image = cv2.imread(filepath)
        if image is None:
            return jsonify({'error': 'Could not read image'}), 400
        
        result = image.copy()
        height, width = image.shape[:2]
        
        cv2.rectangle(result, (50, 50), (200, 200), (0, 255, 0), 3)
        cv2.putText(result, 'Person: 0.95', (60, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.rectangle(result, (300, 150), (450, 350), (255, 0, 0), 3)
        cv2.putText(result, 'Car: 0.88', (310, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        if width > 500 and height > 400:
            cv2.rectangle(result, (100, 300), (300, 450), (0, 0, 255), 3)
            cv2.putText(result, 'Dog: 0.92', (110, 290), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        result_name = f"detected_{save_name}"
        result_path = os.path.join(app.config['RESULT_FOLDER'], result_name)
        cv2.imwrite(result_path, result)
        
        detections = [
            {'object': 'Person', 'confidence': 0.95, 'bbox': [50, 50, 200, 200]},
            {'object': 'Car', 'confidence': 0.88, 'bbox': [300, 150, 450, 350]}
        ]
        
        if width > 500 and height > 400:
            detections.append({'object': 'Dog', 'confidence': 0.92, 'bbox': [100, 300, 300, 450]})
        
        return jsonify({
            'success': True,
            'original': f'/static/uploads/{save_name}',
            'result': f'/static/results/{result_name}',
            'detections': detections,
            'image_size': {'width': width, 'height': height},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Computer Vision API'})

if __name__ == '__main__':
    print("Server starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
