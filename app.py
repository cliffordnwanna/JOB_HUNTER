import streamlit as st
import time
from src.parser import EnhancedCVParser
from src.scraper import JobScraper
from src.matcher import JobMatcher
from src.ui import load_css, show_loading_screen, display_job_card

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Job Hunter Pro",
    page_icon="🎯",
    layout="wide"
)

# Load custom styling
load_css()

def main():
    # Sidebar Navigation
    st.sidebar.image("https://img.icons8.com/clouds/100/000000/job.png", width=100)
    st.sidebar.title("Configuration")
    
    # Matching Mode (Shows Azure AI interest)
    match_mode = st.sidebar.selectbox(
        "Match Engine", 
        ["Standard (TF-IDF)", "Azure Semantic (RAG-based)"],
        help="Azure Semantic requires an Azure OpenAI API Key in settings."
    )
    use_azure = match_mode == "Azure Semantic (RAG-based)"
    
    if use_azure:
        st.sidebar.warning("Note: Azure OpenAI deployment 'text-embedding-3-small' is required.")

    # Governance Section (Sidebar)
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚖️ AI Governance")
    st.sidebar.info("""
    **Privacy & Compliance:**
    - **GDPR Compliant**: No PII is sent to Azure OpenAI.
    - **In-Memory**: No CV data is stored on disk.
    - **Stateless**: Data is purged upon browser exit.
    """)

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Job Hunter</h1>
        <p>AI-Powered Remote Job Matching (Standard + Semantic Matchers)</p>
    </div>
    """, unsafe_allow_html=True)

    # Main UI
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📁 Upload CV")
        uploaded_file = st.file_uploader("Upload your CV (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
        
        if uploaded_file:
            parser = EnhancedCVParser()
            with st.spinner("Parsing CV..."):
                cv_data = parser.parse(uploaded_file.name, uploaded_file.read())
                st.success("✅ CV Parsed successfully!")
                
                with st.expander("Extracted Skills"):
                    st.write(", ".join(cv_data.get('skills', [])))
                
                st.info(f"Experience Found: {cv_data.get('years_experience', 0)} years")

    with col2:
        st.subheader("🎯 Job Matching")
        search_keywords = st.text_input("Enter search keywords (e.g. 'Azure AI', 'Python Developer')", 
                                      placeholder="Leave empty to use CV skills")
        
        if st.button("Find Matching Jobs", type="primary"):
            if not uploaded_file:
                st.error("Please upload your CV first!")
                return

            # Initialize components
            scraper = JobScraper()
            matcher = JobMatcher(cv_data, use_azure=use_azure)
            
            # 1. Scrape
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(pct, text):
                progress_bar.progress(pct)
                status_text.text(text)

            jobs = scraper.scrape_all(
                keywords=[search_keywords] if search_keywords else cv_data.get('skills', []),
                progress_callback=update_progress
            )
            
            if not jobs:
                st.warning("No jobs found with the current criteria. Try broader keywords.")
                return

            # 2. Match & Score
            scored_jobs = matcher.score_jobs(jobs, progress_callback=update_progress)
            
            # Final Results
            update_progress(1.0, "✅ Done! Top matches found.")
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            st.write(f"### Found {len(scored_jobs)} matches for you:")
            
            for job in scored_jobs[:20]:  # Show top 20
                display_job_card(job)

    # Footer for Portfolio
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; font-size: 0.8em;">
        Built by <b>Chukwuma Nwanna</b> | Transitioning to AI Engineer | 
        Powered by Azure OpenAI (Optional) & TF-IDF
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
