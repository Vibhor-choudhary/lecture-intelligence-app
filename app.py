# ============================================================================
# LECTURE INTELLIGENCE - STREAMLIT FRONTEND
# Connects to your Colab backend via ngrok
# ============================================================================

import streamlit as st
import requests
import time
import json

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Lecture Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
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
    }
    .info-box {
        background: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<div class="main-header">🎓 Lecture Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transform lectures into AI-powered study materials</div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - CONFIGURATION
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
    
    st.info("💡 **Tip:** Keep your Colab notebook running for the backend to work!")

# ============================================================================
# MAIN INTERFACE
# ============================================================================

# Input section
youtube_url = st.text_input(
    "📺 YouTube Lecture URL",
    placeholder="https://youtube.com/watch?v=...",
    help="Paste any YouTube lecture URL"
)

# Process button
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
    
    # Clean URL
    backend_url = backend_url.rstrip('/')
    
    # Processing
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
        
        st.success(f"✅ Job started! ID: `{job_id}`")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Poll for completion
        max_attempts = 120  # 10 minutes max
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
                
                # Get results
                lecture_response = requests.get(f"{backend_url}/api/lecture/{job_id}")
                lecture = lecture_response.json()
                
                # Display results
                st.markdown("---")
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(f"### ✅ {lecture['title']}")
                st.markdown(f"**Duration:** {lecture.get('duration', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Tabs for different outputs
                tab1, tab2, tab3, tab4 = st.tabs(["📝 Notes", "❓ Quiz", "📇 Flashcards", "📄 Transcript"])
                
                # Notes tab
                with tab1:
                    notes = lecture['notes']
                    
                    st.subheader("📝 Summary")
                    st.write(notes['summary'])
                    
                    st.subheader("🎯 Key Concepts")
                    for i, concept in enumerate(notes['key_concepts'], 1):
                        st.markdown(f"**{i}.** {concept}")
                    
                    if notes.get('examples'):
                        st.subheader("💡 Examples")
                        for example in notes['examples']:
                            st.markdown(f"• {example}")
                    
                    if notes.get('study_tips'):
                        st.subheader("📚 Study Tips")
                        for tip in notes['study_tips']:
                            st.markdown(f"• {tip}")
                    
                    # Download button
                    notes_text = f"""LECTURE NOTES
{'='*70}
TITLE: {lecture['title']}
DURATION: {lecture.get('duration', 'N/A')}

SUMMARY
{'-'*70}
{notes['summary']}

KEY CONCEPTS
{'-'*70}
""" + '\n'.join([f"{i}. {c}" for i, c in enumerate(notes['key_concepts'], 1)])
                    
                    st.download_button(
                        "⬇️ Download Notes",
                        notes_text,
                        file_name=f"notes_{job_id}.txt",
                        mime="text/plain"
                    )
                
                # Quiz tab
                with tab2:
                    st.subheader(f"❓ Quiz ({len(lecture['quiz'])} Questions)")
                    
                    for q in lecture['quiz']:
                        with st.expander(f"Question {q['num']}: {q['question']}"):
                            st.markdown("**Options:**")
                            for opt, text in q['options'].items():
                                st.markdown(f"**{opt})** {text}")
                            
                            st.success(f"✅ **Correct Answer:** {q['correct']}")
                            st.info(f"**Explanation:** {q['explanation']}")
                    
                    # Download quiz
                    quiz_text = f"""LECTURE QUIZ
{'='*70}
TITLE: {lecture['title']}

"""
                    for q in lecture['quiz']:
                        quiz_text += f"""Q{q['num']}: {q['question']}
A) {q['options']['A']}
B) {q['options']['B']}
C) {q['options']['C']}
D) {q['options']['D']}
Correct: {q['correct']}
Explanation: {q['explanation']}

"""
                    
                    st.download_button(
                        "⬇️ Download Quiz",
                        quiz_text,
                        file_name=f"quiz_{job_id}.txt",
                        mime="text/plain"
                    )
                
                # Flashcards tab
                with tab3:
                    st.subheader(f"📇 Flashcards ({len(lecture['flashcards'])} Cards)")
                    
                    # Display as cards
                    cols = st.columns(2)
                    for i, card in enumerate(lecture['flashcards']):
                        with cols[i % 2]:
                            with st.container():
                                st.markdown(f"**Card {card['num']}**")
                                st.markdown(f"**Q:** {card['front']}")
                                with st.expander("Show Answer"):
                                    st.markdown(f"**A:** {card['back']}")
                    
                    # Download flashcards
                    flash_text = f"""FLASHCARDS
{'='*70}
TITLE: {lecture['title']}

"""
                    for card in lecture['flashcards']:
                        flash_text += f"""Card {card['num']}
Q: {card['front']}
A: {card['back']}

{'='*70}
"""
                    
                    st.download_button(
                        "⬇️ Download Flashcards",
                        flash_text,
                        file_name=f"flashcards_{job_id}.txt",
                        mime="text/plain"
                    )
                
                # Transcript tab
                with tab4:
                    st.subheader("📄 Full Transcript")
                    st.text_area(
                        "Transcript",
                        lecture.get('transcript', 'Not available'),
                        height=400
                    )
                    
                    st.download_button(
                        "⬇️ Download Transcript",
                        lecture.get('transcript', ''),
                        file_name=f"transcript_{job_id}.txt",
                        mime="text/plain"
                    )
                
                break
            
            elif current_status == 'failed':
                st.error(f"❌ Processing failed: {status.get('error', 'Unknown error')}")
                break
        
        else:
            st.warning("⏱️ Processing is taking longer than expected. Check status manually.")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure your Colab notebook is running!")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    Made with ❤️ using Streamlit | Powered by OpenAI Whisper & Google Gemini
</div>
""", unsafe_allow_html=True)
