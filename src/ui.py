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
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            transition: all 0.3s ease;
        }
        .job-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 20px rgba(0,120,212,0.1);
            border-color: #0078D4;
        }
        .job-title {font-size: 1.3em; font-weight: 700; color: #1e1e1e; margin-bottom: 0.5rem;}
        .job-meta {font-size: 0.95em; color: #444; margin: 4px 0;}
        .job-score-container {
            background: #f0f7ff;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            min-width: 100px;
        }
        .job-score {font-size: 1.6em; font-weight: 800; color: #0078D4;}
        .apply-btn {
            display: inline-block;
            text-decoration: none;
            background: #0078D4;
            color: white !important;
            padding: 8px 20px;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: 600;
            margin-top: 12px;
            transition: background 0.2s;
        }
        .apply-btn:hover {
            background: #005a9e;
        }
        .tag {
            background: #eef2f6;
            color: #475569;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-right: 4px;
        }
        
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
        <div style="color: #f0f0f0; font-size: 1.2em;">Initializing AI backend...</div>
    </div>
    """, unsafe_allow_html=True)
    return loading_placeholder

def display_job_card(job: dict):
    score = job.get('Match Score', 0)
    score_color = "#10b981" if score > 75 else "#f59e0b" if score > 50 else "#64748b"

    tags = job.get('tags', [])[:3]
    tags = [str(t) for t in tags if t]
    tag_html = "".join([f'<span class="tag">{t}</span>' for t in tags])

    salary = job.get('salary', 'Not specified')
    if not salary or str(salary).strip() in ('0', ''):
        salary = 'Not disclosed'

    with st.container():
        st.markdown(f"""
        <div class="job-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 20px;">
                <div style="flex: 1;">
                    <div class="job-title">{job.get('title', 'N/A')}</div>
                    <div class="job-meta">🏢 <b>{job.get('company', 'N/A')}</b></div>
                    <div class="job-meta">📍 {job.get('location', 'Remote')} | 💰 {salary}</div>
                    <div class="job-meta">📅 {job.get('posted_date', 'N/A')} | 🌐 {job.get('source', 'API')}</div>
                    <div style="margin-top: 8px;">{tag_html}</div>
                    <a href="{job.get('url', '#')}" target="_blank" class="apply-btn">View Opportunity</a>
                </div>
                <div class="job-score-container">
                    <div style="font-size: 0.75em; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Match</div>
                    <div class="job-score" style="color: {score_color};">{score}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
