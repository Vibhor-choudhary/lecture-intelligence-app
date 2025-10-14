# ============================================================================
# LECTURE INTELLIGENCE - STREAMLIT FRONTEND 
# ============================================================================

import streamlit as st
import requests
import time
import json
import zipfile
import io

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Lecture Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'lecture_data' not in st.session_state:
    st.session_state.lecture_data = None
if 'job_id' not in st.session_state:
    st.session_state.job_id = None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 18px;
        margin-bottom: 40px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 10px;
        padding: 15px 30px;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    .success-box {
        background: #e8f5e9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
        margin-bottom: 20px;
    }
    .quiz-box {
        background: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    .flashcard {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_zip_download(lecture):
    """Create a ZIP file with all outputs"""
    job_id = st.session_state.job_id
    notes = lecture['notes']
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # 1. Notes file
        notes_content = f"""LECTURE NOTES
{'='*70}
TITLE: {lecture['title']}
DURATION: {lecture.get('duration', 'N/A')}

SUMMARY
{'-'*70}
{notes['summary']}

KEY CONCEPTS
{'-'*70}
"""
        for i, concept in enumerate(notes['key_concepts'], 1):
            notes_content += f"\n{i}. {concept}"
        
        if notes.get('examples'):
            notes_content += f"\n\nEXAMPLES\n{'-'*70}\n"
            for ex in notes['examples']:
                notes_content += f"\n• {ex}"
        
        if notes.get('study_tips'):
            notes_content += f"\n\nSTUDY TIPS\n{'-'*70}\n"
            for tip in notes['study_tips']:
                notes_content += f"\n• {tip}"
        
        zip_file.writestr(f'{job_id}_notes.txt', notes_content)
        
        # 2. Quiz file
        quiz_content = f"""LECTURE QUIZ
{'='*70}
TITLE: {lecture['title']}
TOTAL QUESTIONS: {len(lecture['quiz'])}

"""
        for q in lecture['quiz']:
            quiz_content += f"""{'='*70}
QUESTION {q['num']}
{'-'*70}
{q['question']}

OPTIONS:
A) {q['options']['A']}
B) {q['options']['B']}
C) {q['options']['C']}
D) {q['options']['D']}

CORRECT ANSWER: {q['correct']}

EXPLANATION:
{q['explanation']}

"""
        zip_file.writestr(f'{job_id}_quiz.txt', quiz_content)
        
        # 3. Flashcards file
        flash_content = f"""FLASHCARDS
{'='*70}
TITLE: {lecture['title']}
TOTAL CARDS: {len(lecture['flashcards'])}

"""
        for card in lecture['flashcards']:
            flash_content += f"""{'='*70}
CARD {card['num']}
{'-'*70}
FRONT: {card['front']}

BACK: {card['back']}

"""
        zip_file.writestr(f'{job_id}_flashcards.txt', flash_content)
        
        # 4. Transcript
        zip_file.writestr(
            f'{job_id}_transcript.txt',
            f"FULL TRANSCRIPT\n{'='*70}\n\n{lecture.get('transcript', 'Not available')}"
        )
    
    zip_buffer.seek(0)
    return zip_buffer

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<div class="main-header">🎓 Lecture Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transform lectures into AI-powered study materials</div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    backend_url = st.text_input(
        "Backend URL",
        placeholder="https://your-ngrok-url.ngrok-free.app",
        help="Your Colab backend ngrok URL"
    )
    
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get FREE key at: https://aistudio.google.com/app/apikey"
    )
    
    st.divider()
    
    st.subheader("📊 Options")
    num_questions = st.slider("Quiz Questions", 3, 20, 10)
    num_flashcards = st.slider("Flashcards", 5, 30, 15)
    
    st.divider()
    
    # Clear results button
    if st.button("🔄 New Lecture", use_container_width=True):
        st.session_state.lecture_data = None
        st.session_state.job_id = None
        st.rerun()
    
    st.info("💡 **Tip:** Keep your Colab notebook running!")

# ============================================================================
# DOWNLOAD ALL BUTTON (at top if data exists)
# ============================================================================

if st.session_state.lecture_data:
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### ✅ {st.session_state.lecture_data['title']}")
        st.markdown(f"**Duration:** {st.session_state.lecture_data.get('duration', 'N/A')}")
    with col2:
        # Download ALL button
        zip_data = create_zip_download(st.session_state.lecture_data)
        st.download_button(
            label="📥 Download All",
            data=zip_data,
            file_name=f"lecture_{st.session_state.job_id}.zip",
            mime="application/zip",
            use_container_width=True,
            key="download_all_top"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN INTERFACE
# ============================================================================

if not st.session_state.lecture_data:
    # Show input only if no data
    youtube_url = st.text_input(
        "📺 YouTube Lecture URL",
        placeholder="https://youtube.com/watch?v=...",
        help="Paste any YouTube lecture URL"
    )
    
    if st.button("🚀 Generate Study Materials", use_container_width=True):
        
        # Validation
        if not backend_url:
            st.error("❌ Please enter your backend URL in the sidebar")
            st.stop()
        
        if not gemini_key:
            st.error("❌ Please enter your Gemini API key in the sidebar")
            st.stop()
        
        if not youtube_url:
            st.error("❌ Please enter a YouTube URL")
            st.stop()
        
        backend_url = backend_url.rstrip('/')
        
        try:
            # Start job
            with st.spinner("🚀 Starting processing..."):
                response = requests.post(
                    f"{backend_url}/api/process-lecture",
                    json={
                        "youtube_url": youtube_url,
                        "gemini_api_key": gemini_key,
                        "num_questions": num_questions,
                        "num_flashcards": num_flashcards
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    st.error(f"❌ Backend error: {response.text}")
                    st.stop()
                
                job_data = response.json()
                job_id = job_data['job_id']
                st.session_state.job_id = job_id
            
            st.success(f"✅ Job started! ID: `{job_id}`")
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Poll for completion
            max_attempts = 120
            for attempt in range(max_attempts):
                time.sleep(5)
                
                status_response = requests.get(f"{backend_url}/api/job-status/{job_id}")
                status = status_response.json()
                
                current_status = status.get('status', 'unknown')
                progress = status.get('progress', 0)
                
                progress_bar.progress(progress / 100)
                status_text.text(f"📊 Status: {current_status} | Progress: {progress}%")
                
                if current_status == 'completed':
                    st.balloons()
                    
                    # Get and store results
                    lecture_response = requests.get(f"{backend_url}/api/lecture/{job_id}")
                    st.session_state.lecture_data = lecture_response.json()
                    st.rerun()
                
                elif current_status == 'failed':
                    st.error(f"❌ Processing failed: {status.get('error', 'Unknown error')}")
                    break
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure Colab is running!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ============================================================================
# DISPLAY RESULTS (if data exists)
# ============================================================================

if st.session_state.lecture_data:
    lecture = st.session_state.lecture_data
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Notes", "❓ Quiz", "📇 Flashcards", "📄 Transcript"])
    
    # ========================================================================
    # TAB 1: NOTES
    # ========================================================================
    with tab1:
        notes = lecture['notes']
        
        st.subheader("📝 Summary")
        st.write(notes['summary'])
        
        st.divider()
        
        st.subheader("🎯 Key Concepts")
        for i, concept in enumerate(notes['key_concepts'], 1):
            st.markdown(f"**{i}.** {concept}")
        
        if notes.get('examples'):
            st.divider()
            st.subheader("💡 Examples")
            for i, example in enumerate(notes['examples'], 1):
                st.markdown(f"**{i}.** {example}")
        
        if notes.get('study_tips'):
            st.divider()
            st.subheader("📚 Study Tips")
            for i, tip in enumerate(notes['study_tips'], 1):
                st.markdown(f"**{i}.** {tip}")
    
    # ========================================================================
    # TAB 2: QUIZ
    # ========================================================================
    with tab2:
        st.subheader(f"❓ Quiz ({len(lecture['quiz'])} Questions)")
        
        for q in lecture['quiz']:
            st.markdown('<div class="quiz-box">', unsafe_allow_html=True)
            st.markdown(f"### Question {q['num']}")
            st.markdown(f"**{q['question']}**")
            st.markdown("")
            
            # Display options
            for opt, text in q['options'].items():
                if opt == q['correct']:
                    st.success(f"✅ **{opt})** {text}")
                else:
                    st.markdown(f"**{opt})** {text}")
            
            st.markdown("")
            st.info(f"**💡 Explanation:** {q['explanation']}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 3: FLASHCARDS
    # ========================================================================
    with tab3:
        st.subheader(f"📇 Flashcards ({len(lecture['flashcards'])} Cards)")
        
        # Sort flashcards by number
        sorted_cards = sorted(lecture['flashcards'], key=lambda x: x['num'])
        
        # Display in 2 columns
        col1, col2 = st.columns(2)
        
        for i, card in enumerate(sorted_cards):
            target_col = col1 if i % 2 == 0 else col2
            
            with target_col:
                st.markdown('<div class="flashcard">', unsafe_allow_html=True)
                st.markdown(f"**📇 Card {card['num']}**")
                st.markdown(f"**Q:** {card['front']}")
                with st.expander("👁️ Show Answer"):
                    st.markdown(f"**A:** {card['back']}")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 4: TRANSCRIPT
    # ========================================================================
    with tab4:
        st.subheader("📄 Full Transcript")
        st.text_area(
            "Transcript",
            lecture.get('transcript', 'Not available'),
            height=500,
            label_visibility="collapsed"
        )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    Made with ❤️ using Streamlit | Powered by OpenAI Whisper & Google Gemini<br>
    <small>Process lectures • Generate notes • Create quizzes • Make flashcards</small>
</div>
""", unsafe_allow_html=True)
