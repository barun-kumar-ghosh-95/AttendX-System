# 🚀 AttendX AI — Smart Campus & Placement Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)
![DeepFace](https://img.shields.io/badge/DeepFace-Emotion%20AI-orange.svg)
![Status](https://img.shields.io/badge/Status-Live-brightgreen.svg)

**AttendX AI** is an enterprise-grade AI SaaS platform designed for modern campuses. It goes beyond traditional face recognition attendance by integrating real-time classroom analytics, emotion detection, student engagement scoring, and a dedicated Campus Placement Intelligence module.

### 🔗 **[Live Demo on Hugging Face](https://huggingface.co/spaces/barun-kumar-ghosh/AttendX-Syetem)**
*(Note: Please open the direct `hf.space` link provided inside the demo for full camera permissions).*

---

## ✨ Core Features

### 1. 👁️ Live AI Vision (Smart Attendance)
* **Face Recognition:** Instant and secure attendance marking.
* **Emotion & Engagement AI:** Analyzes student emotions in real-time to calculate an "Engagement Score".
* **AI Confidence Metrics:** Real-time distance and confidence percentage for anti-spoofing.
* **Futuristic HUD UI:** Sci-fi inspired targeting boxes and live telemetry data.

### 2. 📊 Command Center (Analytics Dashboard)
* **75% Risk Predictor:** Automatically calculates how many more classes a student needs to reach the safe 75% zone.
* **Real-Time Logs:** View entry time, emotional state, and engagement score instantly.
* **System Metrics:** Tracks total active profiles, average engagement, and system accuracy.

### 3. 🎓 Campus & Placement Intelligence (New)
* **AI Readiness Score:** Evaluates student placement probability.
* **Career Path Predictor:** Suggests roles based on skills and highlights missing technologies.
* **ATS Resume Analyzer:** Mock analysis tool providing ATS scores and optimization tips.
* **Smart Course Engine:** Recommends free courses and YouTube playlists based on skill gaps.
* **Weekend Events Hub:** Tracks campus hackathons, bootcamps, and coding contests.

### 4. 🛡️ Secure 3-Scan Registration
* Optimized fast-enrollment system.
* Takes exactly 3 high-quality captures to create a reliable AI encoding profile.

---

## 💻 Tech Stack

* **Backend:** Python 3, Flask, SQLite
* **AI / ML:** OpenCV, `face_recognition` (dlib), DeepFace (TensorFlow)
* **Frontend:** HTML5, JavaScript (ES6+), TailwindCSS (Glassmorphism & Gradients)
* **Deployment:** Docker, Gunicorn, Hugging Face Spaces (CPU Tier)

---

## ⚙️ How to Use the Live Demo

Since this project is hosted on a Free CPU Server, please follow these steps for the best experience:

1.  **Wake the Server:** If the app hasn't been used in a while, it might take 1-2 minutes to wake up from 'Sleep Mode'.
2.  **Register First:** Because the system uses temporary memory storage to comply with cloud permissions, **data resets on server restart**. Go to **Register Profile**, enter your name, and scan your face 3 times.
3.  **Test the Scanner:** Go to **Live Scanner**, click *Initialize Scanner*, and watch the AI recognize you, detect your emotion, and mark your attendance!
4.  **View Analytics:** Switch to the **Command Center** to see your 75% risk status and logs.

---

## 🛠️ Local Installation

Want to run AttendX AI on your local machine?

**1. Clone the repository:**
```bash
git clone [https://github.com/barun-kumar-ghosh-95/AttendX-System.git](https://github.com/barun-kumar-ghosh-95/AttendX-System.git)
cd AttendX-System
