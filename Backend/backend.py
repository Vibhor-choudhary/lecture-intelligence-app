# ============================================================================
# PRODUCTION BACKEND v3.1 - Fixed Empty Items Issue
# Real Gemini AI Generation with Improved Parsing
# ============================================================================

print("📦 Installing packages...")
!pip install -q flask flask-cors openai-whisper yt-dlp google-generativeai torch pyngrok
print("✅ Installation complete!\n")

from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper, yt_dlp, torch, uuid, threading, json, os
import google.generativeai as genai
from pyngrok import ngrok
from pathlib import Path
import traceback

app = Flask(__name__)
CORS(app)

jobs = {}
whisper_model = None

# Load Whisper
print("🎙️ Loading Whisper model...")
whisper_model = whisper.load_model("tiny")
print("✅ Whisper loaded!\n")

# ============================================================================
# IMPROVED GEMINI AI FUNCTIONS - Filters Empty Items
# ============================================================================

def generate_notes_real(transcript, title, api_key):
    """Generate notes using Gemini - REAL AI with improved parsing"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        prompt = f"""Analyze this lecture:
TITLE: {title}
TRANSCRIPT: {transcript}

Generate:
SUMMARY:
[3-5 paragraphs]

KEY_CONCEPTS:
• [10-15 concepts with detailed explanations]

EXAMPLES:
• [3-5 real-world examples]

STUDY_TIPS:
• [3 actionable study tips]"""

        print(f"  🧠 Calling Gemini for notes...")
        response = model.generate_content(prompt)
        text = response.text
        print(f"  ✅ Got Gemini response ({len(text)} chars)")

        # Parse response with improved filtering
        summary = text.split("KEY_CONCEPTS:")[0].replace("SUMMARY:", "").strip()

        # Extract and filter key concepts (remove empty items)
        kc_section = text.split("KEY_CONCEPTS:")[1].split("EXAMPLES:")[0].strip() if "KEY_CONCEPTS:" in text else ""
        key_concepts = [
            k.strip().lstrip('•-*').strip()
            for k in kc_section.split('\n')
            if k.strip() and k.strip().lstrip('•-*').strip()  # Double check to remove empty
        ]

        # Extract and filter examples
        ex_section = text.split("EXAMPLES:")[1].split("STUDY_TIPS:")[0].strip() if "EXAMPLES:" in text else ""
        examples = [
            e.strip().lstrip('•-*').strip()
            for e in ex_section.split('\n')
            if e.strip() and e.strip().lstrip('•-*').strip()
        ]

        # Extract and filter study tips
        st_section = text.split("STUDY_TIPS:")[1].strip() if "STUDY_TIPS:" in text else ""
        study_tips = [
            s.strip().lstrip('•-*').strip()
            for s in st_section.split('\n')
            if s.strip() and s.strip().lstrip('•-*').strip()
        ]

        # Debug output
        print(f"  📊 Parsed: {len(key_concepts)} concepts, {len(examples)} examples, {len(study_tips)} tips")

        return {
            "summary": summary,
            "key_concepts": key_concepts,
            "examples": examples,
            "study_tips": study_tips
        }
    except Exception as e:
        print(f"  ❌ Notes generation failed: {e}")
        traceback.print_exc()
        return {
            "summary": transcript[:500] if transcript else "Generation failed",
            "key_concepts": [],
            "examples": [],
            "study_tips": []
        }

def generate_quiz_real(transcript, title, num, api_key):
    """Generate quiz using Gemini - REAL AI with improved parsing"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        prompt = f"""Create {num} multiple choice questions based on this lecture:
TITLE: {title}
TRANSCRIPT: {transcript}

Format each question EXACTLY like this:
Q1: [Write complete question here]
A) [Complete option A text]
B) [Complete option B text]
C) [Complete option C text]
D) [Complete option D text]
CORRECT: [Letter]
EXPLANATION: [2-3 sentences explaining why]

Q2: [Next complete question]
...

Make sure every question has meaningful content, not just placeholder text."""

        print(f"  🧠 Calling Gemini for quiz...")
        response = model.generate_content(prompt)
        text = response.text
        print(f"  ✅ Got Gemini response ({len(text)} chars)")

        questions = []
        blocks = text.split('Q')[1:]

        for i, block in enumerate(blocks[:num], 1):
            try:
                lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
                if len(lines) < 6:  # Need Q, A, B, C, D, CORRECT at minimum
                    continue

                # Extract question
                q_line = lines[0]
                question = q_line.split(':', 1)[1].strip() if ':' in q_line else q_line.strip()
                question = question.lstrip('0123456789. ').strip()  # Remove leading numbers

                if not question:
                    continue

                opts = {}
                correct = None
                expl = ""

                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith('A)'):
                        opts['A'] = line[2:].strip()
                    elif line.startswith('B)'):
                        opts['B'] = line[2:].strip()
                    elif line.startswith('C)'):
                        opts['C'] = line[2:].strip()
                    elif line.startswith('D)'):
                        opts['D'] = line[2:].strip()
                    elif line.startswith('CORRECT:'):
                        correct = line.split(':')[1].strip().upper()
                    elif line.startswith('EXPLANATION:'):
                        expl = line.split(':', 1)[1].strip()

                # Only add if we have complete data
                if len(opts) == 4 and correct in ['A', 'B', 'C', 'D'] and question:
                    questions.append({
                        "num": len(questions) + 1,  # Use actual count for proper numbering
                        "question": question,
                        "options": opts,
                        "correct": correct,
                        "explanation": expl if expl else "No explanation provided."
                    })
            except Exception as parse_error:
                print(f"  ⚠️ Failed to parse question {i}: {parse_error}")
                continue

        print(f"  ✅ Generated {len(questions)} quiz questions")
        return questions

    except Exception as e:
        print(f"  ❌ Quiz generation failed: {e}")
        traceback.print_exc()
        return []

def generate_flashcards_real(transcript, title, num, api_key):
    """Generate flashcards using Gemini - REAL AI with improved parsing"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        prompt = f"""Create {num} flashcards for this lecture:
TITLE: {title}
TRANSCRIPT: {transcript}

Format EXACTLY like this:
CARD 1
FRONT: [Write complete question here]
BACK: [Write complete answer here with 2-4 sentences]

CARD 2
FRONT: [Complete question]
BACK: [Complete answer]

Make sure every card has meaningful content on both front and back."""

        print(f"  🧠 Calling Gemini for flashcards...")
        response = model.generate_content(prompt)
        text = response.text
        print(f"  ✅ Got Gemini response ({len(text)} chars)")

        cards = []
        blocks = text.split('CARD ')[1:]

        for i, block in enumerate(blocks[:num], 1):
            try:
                front = ""
                back = ""

                lines = block.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('FRONT:'):
                        front = line.split(':', 1)[1].strip()
                    elif line.startswith('BACK:'):
                        back = line.split(':', 1)[1].strip()

                # Only add if both front and back have content
                if front and back:
                    cards.append({
                        "num": len(cards) + 1,  # Use actual count for proper numbering
                        "front": front,
                        "back": back
                    })
            except Exception as parse_error:
                print(f"  ⚠️ Failed to parse card {i}: {parse_error}")
                continue

        print(f"  ✅ Generated {len(cards)} flashcards")
        return cards

    except Exception as e:
        print(f"  ❌ Flashcard generation failed: {e}")
        traceback.print_exc()
        return []

# ============================================================================
# BACKGROUND PROCESSING
# ============================================================================

def process_lecture_job(job_id, youtube_url, api_key, num_q, num_c):
    """Process lecture in background thread"""
    try:
        print(f"\n🔄 Job {job_id} started")

        # Step 1: Download audio
        jobs[job_id].update({'status': 'downloading', 'progress': 10})
        print(f"📥 Downloading from YouTube...")

        uid = str(uuid.uuid4())[:8]
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': uid,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info.get('title', 'Unknown Video')
            duration = info.get('duration', 0)

        audio_file = f"{uid}.mp3"
        jobs[job_id].update({'progress': 20})
        print(f"✅ Downloaded: {title} ({duration}s)")

        # Step 2: Transcribe with Whisper
        jobs[job_id].update({'status': 'transcribing', 'progress': 30})
        print(f"🎙️ Transcribing audio...")

        result = whisper_model.transcribe(audio_file, language="en", verbose=False, fp16=False)
        transcript = result['text']

        jobs[job_id].update({'progress': 50})
        print(f"✅ Transcribed: {len(transcript)} characters")

        # Step 3: Generate notes with REAL Gemini
        jobs[job_id].update({'status': 'generating_notes', 'progress': 60})
        print(f"📝 Generating AI notes...")

        notes = generate_notes_real(transcript, title, api_key)
        jobs[job_id].update({'progress': 70})
        print(f"✅ Notes: {len(notes['key_concepts'])} concepts")

        # Step 4: Generate quiz with REAL Gemini
        jobs[job_id].update({'status': 'generating_quiz', 'progress': 80})
        print(f"❓ Creating quiz...")

        quiz = generate_quiz_real(transcript, title, num_q, api_key)
        jobs[job_id].update({'progress': 90})
        print(f"✅ Quiz: {len(quiz)} questions")

        # Step 5: Generate flashcards with REAL Gemini
        jobs[job_id].update({'status': 'generating_flashcards', 'progress': 95})
        print(f"📇 Creating flashcards...")

        flashcards = generate_flashcards_real(transcript, title, num_c, api_key)
        print(f"✅ Flashcards: {len(flashcards)} cards")

        # Step 6: Save results
        jobs[job_id].update({
            'status': 'completed',
            'progress': 100,
            'result': {
                'id': job_id,
                'title': title,
                'duration': f"{duration//60}:{duration%60:02d}",
                'notes': notes,
                'quiz': quiz,
                'flashcards': flashcards,
                'transcript': transcript
            }
        })

        print(f"✅ Job {job_id} completed successfully!")

        # Cleanup
        try:
            os.remove(audio_file)
        except:
            pass

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Job {job_id} failed: {error_msg}")
        traceback.print_exc()
        jobs[job_id].update({
            'status': 'failed',
            'error': error_msg,
            'progress': 0
        })

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def home():
    return jsonify({
        'message': 'Lecture Intelligence API',
        'status': 'running',
        'version': '3.1',
        'features': ['transcription', 'real_gemini_ai', 'quiz', 'flashcards'],
        'improvements': ['fixed_empty_items', 'improved_parsing', 'better_error_handling']
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'whisper': 'loaded',
        'model': 'tiny',
        'gemini': 'real_api_calls',
        'jobs_active': len([j for j in jobs.values() if j.get('status') not in ['completed', 'failed']])
    })

@app.route('/api/process-lecture', methods=['POST', 'OPTIONS'])
def process_lecture():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.json
        job_id = str(uuid.uuid4())

        jobs[job_id] = {
            'job_id': job_id,
            'status': 'queued',
            'progress': 0
        }

        thread = threading.Thread(
            target=process_lecture_job,
            args=(
                job_id,
                data['youtube_url'],
                data['gemini_api_key'],
                data.get('num_questions', 10),
                data.get('num_flashcards', 15)
            ),
            daemon=True
        )
        thread.start()

        return jsonify({'job_id': job_id, 'estimated_time': 120})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/job-status/<job_id>')
def job_status(job_id):
    if job_id in jobs:
        return jsonify(jobs[job_id])
    return jsonify({'error': 'Job not found'}), 404

@app.route('/api/lecture/<job_id>')
def get_lecture(job_id):
    if job_id in jobs and jobs[job_id].get('status') == 'completed':
        return jsonify(jobs[job_id]['result'])
    return jsonify({'error': 'Not ready or not found'}), 404

# ============================================================================
# START SERVER
# ============================================================================

print("="*70)
print("🚀 LECTURE INTELLIGENCE BACKEND v3.1")
print("✨ Improvements: Fixed empty items, better parsing")
print("="*70)

print("\n🔑 Ngrok Token Setup")
print("Get FREE token: https://dashboard.ngrok.com/get-started/your-authtoken\n")
token = input("Paste token: ").strip()

if not token:
    print("❌ No token provided")
    exit()

try:
    ngrok.set_auth_token(token)
    public_url = ngrok.connect(5000)
    print(f"\n✅ PUBLIC URL: {public_url}")
    print(f"📋 Copy this URL for your frontend")
    print(f"🩺 Health: {public_url}/health")
except Exception as e:
    print(f"❌ Ngrok error: {e}")
    exit()

print("\n" + "="*70)
print("✨ BACKEND LIVE - v3.1 with Fixed Parsing")
print("="*70 + "\n")

try:
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
except KeyboardInterrupt:
    print("\n🛑 Backend stopped")
except Exception as e:
    print(f"\n❌ Server error: {e}")
    traceback.print_exc()
