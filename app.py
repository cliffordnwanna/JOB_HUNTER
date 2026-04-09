import streamlit as st
import pandas as pd
import time
import sys
import os
import re
import html

# Ensure the 'src' directory is in the Python path for Hugging Face
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parser_v2 import EnhancedCVParser
from src.scraper import JobScraper
from src.matcher_v2 import JobMatcher
from src.ui import load_css, show_loading_screen, display_job_card
from src.model_manager import warmup_on_startup

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
    # Cold start tracking (for analytics)
    if "first_load" not in st.session_state:
        st.session_state.first_load = True
    
    # Session state guard for model warmup (prevents rerun crashes)
    if "models_loaded" not in st.session_state:
        with st.spinner("🚀 Loading AI models (one-time, ~20s on cold start)..."):
            try:
                warmup_on_startup(['bert'])
                st.session_state.models_loaded = True
                st.sidebar.success("✅ AI models ready")
            except Exception:
                st.session_state.models_loaded = False
                st.sidebar.info("ℹ️ Running in fast mode (TF-IDF only)")
    # Sidebar Navigation
    st.sidebar.image("https://img.icons8.com/clouds/100/000000/job.png", width=100)
    st.sidebar.title("Configuration")
    
    # Matching Mode Selection - Default to TF-IDF for HF Free Tier performance
    match_mode_display = st.sidebar.selectbox(
        "Match Engine", 
        ["Standard (TF-IDF)", "BERT Semantic (Local AI)", "Azure Semantic (Cloud)", "Hybrid (All Combined)"],
        index=0,  # Default to TF-IDF for fastest response on HF Free Tier
        help="TF-IDF = fastest (recommended for HF Free Tier). BERT = better accuracy but slower. Azure = requires API key."
    )
    
    # Map display to internal mode
    match_mode_map = {
        "Standard (TF-IDF)": "tfidf",
        "BERT Semantic (Local AI)": "bert",
        "Azure Semantic (Cloud)": "azure",
        "Hybrid (All Combined)": "hybrid"
    }
    match_mode = match_mode_map[match_mode_display]
    
    # API Key validation at selection time (prevents mid-match crashes)
    if match_mode in ["azure", "hybrid"]:
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not azure_key or not azure_endpoint:
            st.sidebar.error("⚠️ Azure mode selected but API key/endpoint missing. Switching to BERT fallback.")
            match_mode = "bert" if match_mode == "azure" else "bert"  # Fallback
        else:
            st.sidebar.success("✅ Azure OpenAI configured")
    
    # Show appropriate warnings
    if match_mode == "bert":
        st.sidebar.info("BERT: Uses local transformer model (~80MB).")
    elif match_mode == "hybrid":
        st.sidebar.info("Hybrid: TF-IDF + BERT (+ Azure if configured).")
    elif match_mode == "tfidf":
        st.sidebar.info("TF-IDF: Fast keyword matching, no ML models.")

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

    # Main UI - Vertical Layout (CV Upload on top, Job Matching below)
    st.markdown("---")
    st.subheader("📁 Step 1: Upload Your CV")
    uploaded_file = st.file_uploader("Upload your CV (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file:
        # Store file bytes once to avoid double read() and EOF issues
        file_bytes = uploaded_file.read()
        file_hash = hash(file_bytes)
        
        # Check if this is a new file (prevent stale session state)
        if file_hash != st.session_state.get("cv_file_hash"):
            parser = EnhancedCVParser()
            with st.spinner("🔍 Parsing CV with AI..."):
                st.session_state.cv_data = parser.parse(uploaded_file.name, file_bytes)
                st.session_state.cv_file_hash = file_hash
            
        # Show extraction results
        cv_data = st.session_state.cv_data
        skills = cv_data.get('skills', [])
        years_exp = cv_data.get('years_experience', 0)
        professional_title = cv_data.get('professional_title', '')
        
        # Notify user if using fallback extraction
        extraction_method = cv_data.get('extraction_method', '')
        if extraction_method in ['llm_error', 'llm_failed', 'local_fallback']:
            st.info("ℹ️ Using local extraction mode. Results may be less precise.")
        
        if skills:
            st.success(f"✅ CV Parsed! Found **{len(skills)} skills** and **{years_exp} years** experience")
            with st.expander("📋 View Extracted Profile", expanded=True):
                # Show professional title if available
                if professional_title:
                    st.markdown(f"**👤 Professional Title:** {professional_title}")
                
                # Show skills
                skill_text = ", ".join(skills[:30])  # Limit display
                st.markdown(f"**🛠️ Skills:** {skill_text}")
                
                # Show extraction confidence
                confidence = cv_data.get('extraction_confidence', 0)
                if confidence:
                    st.progress(confidence, text=f"Extraction confidence: {confidence:.0%}")
        else:
            st.warning("⚠️ No skills were extracted. Try uploading a different CV format or check the file content.")
    
    st.markdown("---")
    st.subheader("🎯 Step 2: Find Matching Jobs")
    
    # Filter Section
    with st.expander("🔍 Search Filters & Options", expanded=False):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            search_keywords = st.text_input("Job Title / Skills", 
                                          placeholder="e.g. 'Physiotherapist', 'Physical Therapist', 'Remote Healthcare'",
                                          help="Leave empty to use skills extracted from your CV")
            limit = st.slider("Max results per source", 10, 100, 50)
        with f_col2:
            location_filter = st.selectbox("Preferred Location", ["All Remote", "USA", "Europe", "UK", "Worldwide"])
            min_score = st.slider("Minimum Match Score %", 10, 100, 30)

    if st.button("Find Matching Jobs", type="primary", use_container_width=True):
        if not uploaded_file:
            st.error("Please upload your CV first!")
            return

        # Initialize components
        cv_data = st.session_state.get('cv_data')
        if not cv_data:
            st.error("CV data not found. Please re-upload your CV.")
            return
            
        scraper = JobScraper()
        matcher = JobMatcher(cv_data, match_mode=match_mode)
        
        # 1. Scrape
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(pct, text):
            progress_bar.progress(pct)
            status_text.text(text)

        # Use search keywords or CV skills (strip whitespace)
        search_keywords = search_keywords.strip() if search_keywords else ""
        keywords = [search_keywords] if search_keywords else cv_data.get('skills', [])
        if not keywords:
            keywords = ['remote']  # fallback
        
        # Cache key for scraper results (avoid rescraping same query)
        cache_key = f"{str(keywords)}_{limit}_{location_filter}"
        
        if cache_key != st.session_state.get("last_search_key"):
            # New search - scrape fresh
            with st.spinner("⏱️ Searching job boards (20-40s on first search)..."):
                jobs = scraper.scrape_all(
                    keywords=keywords,
                    limit=limit,
                    progress_callback=update_progress,
                    timeout=10
                )
                st.session_state.cached_jobs = jobs
                st.session_state.last_search_key = cache_key
        else:
            # Use cached results
            jobs = st.session_state.get("cached_jobs", [])
            st.info("📋 Using cached results. Refresh page to search again.")
        
        if not jobs:
            st.error("⚠️ No jobs could be retrieved. This may be due to:")
            st.markdown("""
            - Network timeout (common on HuggingFace Free Tier)
            - All job boards temporarily unavailable
            
            **Try:**
            1. Wait a moment and click "Find Matching Jobs" again
            2. Use cached results if available (refresh page)
            3. Run locally for more reliable scraping
            """)
            return

        # 2. Match & Score
        scored_jobs = matcher.score_jobs(jobs, progress_callback=update_progress)
        
        # Apply Filters
        if location_filter != "All Remote":
            scored_jobs = [j for j in scored_jobs if location_filter.lower() in j.get('location', '').lower()]
        
        filtered_by_score = [j for j in scored_jobs if j.get('Match Score', 0) >= min_score]
        
        # Suggest lowering threshold if everything filtered out
        if not filtered_by_score and scored_jobs:
            max_available = max(j.get('Match Score', 0) for j in scored_jobs)
            st.warning(f"⚠️ No jobs matched above {min_score}% score. "
                      f"Maximum available score is {max_available:.0f}%. "
                      f"Try lowering the minimum score threshold.")
            # Show unfiltered results instead
            filtered_by_score = scored_jobs[:10]  # Show top 10 anyway
        
        scored_jobs = filtered_by_score

        # Final Results
        update_progress(1.0, "✅ Done! Top matches found.")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        st.write(f"### Found {len(scored_jobs)} matches for you (showing top 20):")
        st.caption("💡 All matches are included in the CSV download below")
        
        # Download as CSV Utility (includes ALL matches, not just displayed)
        import html
        
        df = pd.DataFrame(scored_jobs)
        if not df.empty:
            # Clean up description for CSV readability - strip HTML tags
            if 'description' in df.columns:
                # Remove HTML tags, decode entities, truncate
                df['description'] = df['description'].astype(str).apply(
                    lambda x: html.unescape(re.sub(r'<[^>]+>', '', x))[:200] + "..."
                )
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Matches as CSV",
                data=csv,
                file_name=f"job_matches_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Export your matches for application tracking"
            )
        
        for job in scored_jobs[:20]:  # Show top 20
            display_job_card(job)

    # Footer for Portfolio
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; font-size: 0.8em;">
        Built by <b>Chukwuma Clifford Nwanna</b>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
