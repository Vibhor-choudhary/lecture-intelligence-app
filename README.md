<div align="center">

# 🎓 Lecture Intelligence
**Transform any lecture into AI-powered study materials**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

[Live Demo](https://lecture-intelligence-app-38iblrempnyc28kdukruik.streamlit.app/) • [Documentation](docs/) • [Report Bug](issues) • [Request Feature](issues)

</div>

---

## 📖 Table of Contents
- [About](#about)
- [Features](#features)
- [Demo](#demo)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 About
**Lecture Intelligence** automatically transforms any lecture video into complete, AI-generated study materials:
- 📝 **Detailed Notes** with key concepts and examples  
- ❓ **Interactive Quizzes** with explanations  
- 📇 **Flashcards** for spaced repetition  
- 📄 **Full Transcripts**

Ideal for students and educators seeking efficient learning tools.

---

## ✨ Features
### 🤖 AI-Powered
- **Whisper** → Speech-to-text  
- **Google Gemini 2.0** → Notes, Quizzes & Flashcards generation  
- Handles 5 seconds – 2 hour long lectures

### 🎨 Streamlit UI
- Clean, simple, and responsive  
- Real-time progress tracking  
- Download results as ZIP

### 🔒 Privacy
- No permanent data storage  
- Local or Colab backend support  

---

## 🚀 Quick Start

### Prerequisites
```bash
python --version   # 3.8+
pip --version

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Vibhor-choudhary/lecture-intelligence-app.git

### 2️⃣ Install Frontend Dependencies

Install all frontend libraries required by **Streamlit**:

```bash
pip install -r requirements.txt
If you encounter permission errors, use:

bash
Copy code
pip install -r requirements.txt --user

3️⃣ Get API Keys (FREE)
🧠 Google Gemini API Key

This key allows the app to generate notes, quizzes, and flashcards using Google’s AI.

Steps to get it:

Go to https://aistudio.google.com/app/apikey

Click “Create API Key”

Copy your key (looks like AIza...)

You’ll use this key inside the app sidebar or as an environment variable

🌐 Ngrok Token (For Backend)

Ngrok creates a public HTTPS URL for your backend when running locally or in Colab.

Steps to get it:

Visit https://dashboard.ngrok.com/signup

Sign up (no credit card required)

After logging in, go to
👉 https://dashboard.ngrok.com/get-started/your-authtoken

Copy your token (looks like 2GgYxxxxxx)

Keep it ready for the backend setup

4️⃣ Start the Backend

You have two options to run your backend:
(Choose one depending on your setup preference.)

Option A: Google Colab (Recommended for Beginners)

Open the provided Colab notebook:
📘 colab/backend_colab.ipynb

Click Runtime → Run all

Paste your ngrok token when prompted

After setup, you’ll see a line like:

🔗 Public URL: https://1234abcd.ngrok-free.app


This is your backend API endpoint — copy it!

Option B: Local Machine Setup

Run the Flask backend locally on your computer:

cd backend
pip install -r requirements.txt
python backend.py


When the backend starts, Ngrok will automatically generate a public URL (for example):

https://random-id.ngrok-free.app


Keep this URL safe — you’ll need it later in the Streamlit app.

5️⃣ Start the Frontend

Now that your backend is running, open the Streamlit frontend:

streamlit run app.py


Once it starts, Streamlit will display:

Local URL: http://localhost:8501
Network URL: http://<your-ip>:8501


Click the link or open it manually in your browser.

6️⃣ Using the App (Step-by-Step)

Paste your backend URL (from Colab or Ngrok)

Paste your Google Gemini API key

Enter a YouTube lecture URL (e.g., a recorded lecture or talk)

Adjust optional parameters:

Number of quiz questions: default → 10

Number of flashcards: default → 15

Click “Generate Study Materials”

⏱️ Wait 2–5 minutes (depending on lecture length and model).
The app will show progress and then display:

📝 AI-generated Notes

❓ Interactive Quizzes

📇 Flashcards for revision

📄 Full Transcript

You can also download all materials as a ZIP file.

7️⃣ Folder Structure Overview
lecture-intelligence/
├── app.py                    # Streamlit frontend
├── backend/
│   ├── backend.py             # Flask backend
│   ├── requirements.txt       # Backend dependencies
│   └── README.md
├── colab/
│   └── backend_colab.ipynb    # Colab backend notebook
├── docs/
│   ├── setup-guide.md
│   ├── api-documentation.md
│   └── deployment-guide.md
├── assets/
│   ├── screenshots/
│   └── demo/
├── examples/
│   ├── sample-notes.txt
│   ├── sample-quiz.txt
│   └── sample-flashcards.txt
├── requirements.txt           # Frontend dependencies
├── LICENSE
└── .gitignore

8️⃣ Environment Variables (Optional)

You can store your keys securely using a .env file.

Create a new file named .env in the root directory:

GEMINI_API_KEY=your-key-here
NGROK_TOKEN=your-token-here


💡 Tip: Never upload your .env file or API keys to GitHub.
Always add .env to your .gitignore (already included by default).

---

### 9️⃣ Test the Backend API (Optional)

You can test your backend endpoints directly using **curl** or **Postman** to confirm that the Flask server and ngrok tunnel are working correctly.

---

#### ▶️ Start Lecture Processing

```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/api/process-lecture \
  -H "Content-Type: application/json" \
  -d '{
        "youtube_url": "https://youtube.com/watch?v=abc123",
        "gemini_api_key": "AIza-yourkey",
        "num_questions": 10,
        "num_flashcards": 15
      }'
Example Response:

json
Copy code
{
  "job_id": "xyz-789",
  "estimated_time": 120
}
🟢 Check Job Status
bash
Copy code
curl https://your-ngrok-url.ngrok-free.app/api/job-status/xyz-789
Example Response:

json
Copy code
{
  "status": "transcribing",
  "progress": 65
}
📄 Retrieve Final Results
bash
Copy code
curl https://your-ngrok-url.ngrok-free.app/api/lecture/xyz-789
Example Response:

json
Copy code
{
  "id": "xyz-789",
  "title": "AI Lecture Basics",
  "notes": { "summary": "..." },
  "quiz": [ { "question": "...", "options": [...] } ],
  "flashcards": [ { "front": "...", "back": "..." } ],
  "transcript": "Full lecture transcript here..."
}
🔄 Common Issues & Fixes
❌ Issue	🧩 Cause	🛠️ Fix / Solution
Ngrok tunnel expired	Free ngrok session timed out (2 hours limit)	Restart backend or rerun Colab notebook to get a new public URL
Gemini API key invalid	Key revoked or mistyped	Generate a new one at aistudio.google.com/app/apikey
YouTube download failed	Private, restricted, or unavailable video	Use a public video or update yt-dlp: pip install --upgrade yt-dlp
Backend not reachable	Wrong ngrok URL or session ended	Use the latest printed URL from backend logs
Whisper model error	Insufficient RAM	Switch to "tiny" model in backend.py
App stuck at 0%	Gemini request taking time	Wait 1–2 minutes or reduce lecture length
ModuleNotFoundError	Missing dependencies	Run pip install -r requirements.txt again

🧾 Logs (Backend Console Preview)
When running the backend (in Colab or locally), you’ll see real-time logs:

yaml
Copy code
🔄 Job abc123 started
📥 Downloading from YouTube...
✅ Downloaded: AI Lecture (320s)
🎙️ Transcribing audio...
✅ Transcribed: 1,540 characters
🧠 Generating AI notes...
✅ Gemini generated 3,200 chars
✅ Job abc123 completed successfully!
If you don’t see any “✅” completion messages, check the error logs printed in red — they’ll specify the cause (e.g., API key issue or rate limit).

✅ Verification Checklist
Before using or deploying your project, make sure all these are working:

✅	Task
☐	Frontend (Streamlit) runs successfully on localhost:8501
☐	Backend (Flask) returns a valid public ngrok URL
☐	Gemini API key verified and functional
☐	YouTube video successfully downloads and transcribes
☐	Generated notes, quizzes, and flashcards display properly
☐	ZIP download button works correctly
☐	No sensitive data (API keys, .env) committed to GitHub

💡 Tips for Best Performance
Use Google Colab GPU runtime for faster Whisper transcription
(Runtime → Change runtime type → GPU)

Use the "base" Whisper model for best accuracy/speed balance

Keep lecture videos under 60 minutes for free Colab use

Restart backend every few hours to refresh ngrok connection

Always test using short videos before longer lectures

🏁 You’re All Set!
You now have a fully working Lecture Intelligence setup:

Streamlit Frontend → User interface

Flask Backend → AI processing hub

Google Gemini + Whisper → Study material generation

🚀 You can now deploy, share, and demo your project confidently!

⭐ Star the Repo
If you found this project helpful, please ⭐ star this repository to support future development!

🔗 Useful Links
📘 Setup Guide

📡 API Documentation

🚢 Deployment Guide

🛠️ Backend Docs

<div align="center">
Made with ❤️ by Your Name
⬆ Back to Top

</div> ```
