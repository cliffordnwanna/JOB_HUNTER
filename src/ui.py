import streamlit as st

def load_css():
    st.markdown("""
    <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Mobile-friendly padding */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Prominent header */
        .main-header {
            background: linear-gradient(135deg, #0078D4 0%, #004578 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .main-header h1 {
            color: white;
            margin: 0;
            font-size: 2em;
            font-weight: 700;
        }
        .main-header p {
            color: #f0f0f0;
            margin: 8px 0 0 0;
            font-size: 1em;
        }
        
        /* Job card styles */
        .job-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-left: 5px solid #0078D4;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .job-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .job-title {font-size: 1.2em; font-weight: 600; color: #333; margin-bottom: 0.3rem;}
        .job-meta {font-size: 0.9em; color: #666;}
        .job-score {font-size: 1.5em; font-weight: bold; color: #0078D4;}
        
        /* Azure-themed success box */
        .stSuccess {
            background-color: #f0f8ff;
            border-left-color: #0078D4;
        }
    </style>
    """, unsafe_allow_html=True)

def show_loading_screen():
    loading_placeholder = st.empty()
    loading_placeholder.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; background: linear-gradient(135deg, #0078D4 0%, #004578 100%); border-radius: 20px; margin: 20px;">
        <div style="color: white; font-size: 2.5em; margin-bottom: 15px; font-weight: bold;">🚀 Job Hunter</div>
        <div style="color: #f0f0f0; font-size: 1.2em;">Initializing Azure AI Backend...</div>
    </div>
    """, unsafe_allow_html=True)
    return loading_placeholder

def display_job_card(job: dict):
    score = job.get('Match Score', 0)
    score_color = "#4CAF50" if score > 75 else "#FF9800" if score > 50 else "#999"
    
    with st.container():
        st.markdown(f"""
        <div class="job-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div class="job-title">{job.get('title', 'N/A')}</div>
                    <div class="job-meta">🏢 {job.get('company', 'N/A')} | 📍 {job.get('location', 'Remote')}</div>
                    <div class="job-meta">💰 {job.get('salary', 'Not specified')} | 📅 {job.get('posted_date', 'N/A')}</div>
                    <div style="margin-top: 10px;">
                        <a href="{job.get('url', '#')}" target="_blank" style="text-decoration: none; background-color: #0078D4; color: white; padding: 5px 15px; border-radius: 5px; font-size: 0.9em;">View Job</a>
                    </div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.8em; color: #666;">Match Score</div>
                    <div class="job-score" style="color: {score_color};">{score}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
