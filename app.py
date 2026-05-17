import sys
import os
import io
import tempfile
import traceback
import re
import time
from flask import Flask, render_template, request, jsonify
import base64
import cv2
import face_recognition
import numpy as np
import sqlite3
from datetime import datetime
import math
from pathlib import Path
from deepface import DeepFace

# Fix Windows console encoding for DeepFace
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

app = Flask(__name__)

# SETUP DATABASE IN TEMP DIR
DB_FILE = str(Path(tempfile.gettempdir()) / "attendx_ai.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            emotion TEXT DEFAULT '',
            engagement_score INTEGER DEFAULT 0,
            confidence_score INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# SETUP DATASET
DATASET_DIR = Path(tempfile.gettempdir()) / "dataset_ai"
DATASET_DIR.mkdir(parents=True, exist_ok=True)

known_encodings = []
known_names = []

print("Initializing AttendX AI Core...")
for person_name in os.listdir(DATASET_DIR):
    person_path = DATASET_DIR / person_name
    if not person_path.is_dir(): continue
    for image_name in os.listdir(person_path):
        try:
            image = face_recognition.load_image_file(person_path / image_name)
            encodings = face_recognition.face_encodings(image)
            if len(encodings) > 0:
                known_encodings.append(encodings[0])
                known_names.append(person_name.replace('_', ' '))
        except Exception:
            continue
print(f"Loaded {len(known_encodings)} AI Profiles.")

analysis_cache = {}

def get_cached_analysis(name):
    if name in analysis_cache:
        entry = analysis_cache[name]
        if entry.get("count", 0) >= 3:
            return entry
        if time.time() - entry["timestamp"] < 10:
            return entry
    return None

def run_deepface_analysis(face_img):
    try:
        if face_img.shape[0] > 224 or face_img.shape[1] > 224:
            face_img = cv2.resize(face_img, (224, 224))
        results = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False, detector_backend='skip', silent=True)
        result = results[0] if isinstance(results, list) else results
        emotion = result.get("dominant_emotion", "neutral")
        
        engagement = 50
        if emotion in ['happy', 'surprise']: engagement = 95
        elif emotion == 'neutral': engagement = 75
        elif emotion in ['sad', 'fear', 'disgust']: engagement = 30
        elif emotion == 'angry': engagement = 10

        return {"emotion": emotion, "engagement": engagement, "timestamp": time.time()}
    except Exception:
        return None

marked_names = set()

def mark_attendance(name, analysis_data, distance):
    today = datetime.now().strftime("%Y-%m-%d")
    log_key = f"{name}_{today}"
    
    if log_key not in marked_names:
        marked_names.add(log_key)
        now = datetime.now()
        
        emotion = analysis_data.get("emotion", "neutral") if analysis_data else "neutral"
        engagement = analysis_data.get("engagement", 50) if analysis_data else 50
        confidence = max(0, min(100, int((1.0 - distance) * 100)))

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attendance_logs (name, date, time, emotion, engagement_score, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, today, now.strftime("%I:%M %p"), emotion, engagement, confidence))
        conn.commit()
        conn.close()

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.json['image']
        header, encoded = data.split(",", 1)
        frame = cv2.imdecode(np.frombuffer(base64.b64decode(encoded), np.uint8), cv2.IMREAD_COLOR)

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        faces_analysis = [] 

        for face_encoding, face_location in zip(face_encodings, face_locations):
            name = "Unknown"
            best_distance = 1.0
            
            if len(known_encodings) > 0:
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < 0.5:
                    name = known_names[best_match_index]
                    best_distance = face_distances[best_match_index]

            top, right, bottom, left = [coord * 4 for coord in face_location]
            h, w = frame.shape[:2]
            pad = 20
            face_crop = frame[max(0, top-pad):min(h, bottom+pad), max(0, left-pad):min(w, right+pad)]

            analysis = get_cached_analysis(name)
            if analysis is None and face_crop.size > 0:
                analysis = run_deepface_analysis(face_crop)
                if analysis:
                    analysis["count"] = analysis_cache.get(name, {}).get("count", 0) + 1
                    analysis_cache[name] = analysis

            if name != "Unknown":
                mark_attendance(name, analysis, best_distance)

            color = (0, 215, 255) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            length = 15
            cv2.line(frame, (left, top), (left+length, top), color, 4)
            cv2.line(frame, (left, top), (left, top+length), color, 4)

            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            face_data = {"name": name}
            if analysis:
                face_data["analysis"] = {
                    "emotion": analysis.get("emotion", "N/A"),
                    "engagement": analysis.get("engagement", 0),
                    "confidence": max(0, min(100, int((1.0 - best_distance) * 100))) if name != "Unknown" else 0
                }
            faces_analysis.append(face_data)

        _, buffer = cv2.imencode('.jpg', frame)
        return jsonify({'image': f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}", 'faces': faces_analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    MIN_PHOTOS = 3
    try:
        payload = request.json
        name = payload.get('name', '').strip()
        images_data = payload.get('images', [])[:3] 

        if not name or len(images_data) < MIN_PHOTOS:
            return jsonify({'success': False, 'error': 'Invalid name or insufficient photos.'}), 400

        person_dir = DATASET_DIR / name.replace(' ', '_')
        person_dir.mkdir(parents=True, exist_ok=True)

        new_enc = []
        for idx, img_data in enumerate(images_data):
            frame = cv2.imdecode(np.frombuffer(base64.b64decode(img_data.split(',')[1]), np.uint8), cv2.IMREAD_COLOR)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locs = face_recognition.face_locations(rgb)
            if len(locs) == 1:
                new_enc.append(face_recognition.face_encodings(rgb, locs)[0])
                cv2.imwrite(str(person_dir / f"p_{idx}.jpg"), frame)

        if len(new_enc) < MIN_PHOTOS:
            return jsonify({'success': False, 'error': 'Face not clear in photos.'}), 400

        for enc in new_enc:
            known_encodings.append(enc)
            known_names.append(name)

        return jsonify({'success': True, 'message': f'Profile for {name} activated.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard_data')
def dashboard_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, time, emotion, engagement_score, confidence_score FROM attendance_logs ORDER BY id DESC LIMIT 10")
    logs = [{"name": r[0], "time": r[1], "emotion": r[2], "engagement": r[3], "confidence": r[4]} for r in cursor.fetchall()]
    
    TOTAL_CLASSES = 100
    cursor.execute("SELECT name, COUNT(*) FROM attendance_logs GROUP BY name")
    attendance_counts = cursor.fetchall()
    
    students = []
    for name, attended in attendance_counts:
        pct = round((attended / TOTAL_CLASSES) * 100, 1)
        needed = max(0, math.ceil(((0.75 * TOTAL_CLASSES) - attended) / 0.25)) if pct < 75 else 0
        status = "Risk" if pct < 75 else "Safe"
        students.append({"name": name, "pct": pct, "needed": needed, "status": status})
        
    conn.close()
    return jsonify({"logs": logs, "analytics": students})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)
