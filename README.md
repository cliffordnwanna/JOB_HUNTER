---
title: Job Hunter Pro
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.28.0"
app_file: app.py
pinned: false
---

# 🚀 Job Hunter Pro: Dynamic AI Job Matching Platform

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/cliffordnwanna/job-hunter)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://remotejobhunter.streamlit.app)

**Job Hunter Pro** is a production-grade AI platform featuring **LLM-powered structured extraction**, **PII tokenization**, and **graceful degradation chain** (Azure → BERT → TF-IDF → spaCy). Built with privacy-first architecture — no hardcoded skill databases, explicit job title extraction, and GDPR Article 17 compliant immediate PII purge.

---

## 🌐 Live Project
**🚀 [Try Job Hunter on Hugging Face Spaces](https://huggingface.co/spaces/cliffordnwanna/job-hunter)**

---

## ⚖️ AI Governance & Data Privacy (GDPR Compliant)

As an AI Engineer, I prioritize **Responsible AI** and data sovereignty:

- **PII Sanitization**: Emails, phones, names automatically detected and masked as `[EMAIL_1]`, `[PHONE_1]`, `[NAME_1]` before any LLM processing
- **Immediate Purge**: PII vault is overwritten and cleared immediately after sanitization (GDPR Article 17 compliant)
- **Zero Data Persistence**: No CV data, skills, or PII stored to disk or databases
- **Privacy-First Design**: Sanitized text only sent to LLM; original PII never leaves your session

---

## 🆕 What's New in v2.0

### Dynamic LLM-Based Extraction
Unlike traditional parsers with hardcoded skill databases, Job Hunter Pro uses **Azure OpenAI** to dynamically extract skills for ANY profession:
- ✅ Works for physiotherapists, chefs, financial analysts — no pre-defined lists
- ✅ Extracts explicit job titles from CV header (not inferred)
- ✅ Structured JSON output: skills, domain, career level, tools
- ✅ Falls back to local spaCy NER if LLM unavailable

### Local AI Semantic Matching
- **BERT Matcher** (`all-MiniLM-L6-v2`): Runs entirely locally, no API key needed
- **Model Caching**: `@st.cache_resource` ensures one-time download, persistent across sessions
- **Hybrid Scoring**: TF-IDF + BERT + Azure embeddings weighted intelligently

---

## Project Overview

### 🛑 The Problem
Traditional job parsers fail because they rely on hardcoded skill databases that only cover tech roles. A physiotherapist's CV gets misclassified because "manual therapy" and "gait analysis" aren't in the keyword list.

### 💡 The Solution
**Job Hunter Pro** uses **dynamic LLM extraction** with **PII sanitization**:
1. CV uploaded → PII masked (emails, phones, names)
2. Sanitized text sent to LLM → Structured skill extraction
3. PII immediately purged → GDPR compliant
4. Dynamic matching across 6+ job boards

### 📈 The Impact
- **Universal**: Dynamic skill extraction works for healthcare, finance, creative, tech — any profession
- **Accurate**: Extracts explicit job titles from CV header (fallback to inference only if missing)
- **Private**: PII tokenized (`[EMAIL_1]`, `[NAME_1]`) before LLM, vault purged immediately (GDPR Article 17)
- **Fast**: `@st.cache_resource` model singleton, parallel scraping with timeouts, warm-start on app load
- **Robust**: Graceful degradation chain ensures matching even if Azure/BERT unavailable

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[User CV Upload] --> B[Text Extraction]
    B --> C[PII Sanitizer]
    C -->|Mask: [EMAIL_1], [NAME_1]| D[Sanitized Text]
    C -->|Immediate Purge| E[PII Vault Cleared]
    D --> F[LLM Extractor]
    F -->|Structured JSON| G[Skills, Title, Domain]
    H[Job Boards] --> I[Multi-Source Scraper]
    I --> J[Deduplication]
    G --> K{Dynamic Matcher}
    J --> K
    K -->|Fast| L[TF-IDF]
    K -->|Local AI| M[BERT Semantic]
    K -->|Cloud| N[Azure OpenAI]
    L --> O[Weighted Score]
    M --> O
    N --> O
    O --> P[Ranked Job Matches]
```

---

## Key Technical Highlights

### 🔒 Privacy-First Pipeline (GDPR Article 17)
- **PII Tokenization**: Emails, phones, names masked as `[EMAIL_1]`, `[PHONE_1]`, `[NAME_1]` before any LLM call
- **Immediate Purge**: `extract_and_purge()` overwrites vault with `[REDACTED]` then clears — PII never persists
- **Zero Storage**: No CV data, skills, or tokens written to disk or database

### 🤖 LLM-Powered Structured Extraction
- **Pydantic Output Schema**: Structured JSON with skills, professional_title, domain, career_level, tools_software
- **Zero Hardcoded Skills**: LLM extracts dynamically from context — no pre-defined keyword lists
- **Explicit Job Titles**: Extracted from CV header/summary, inference only as fallback
- **Domain Agnostic**: Healthcare, finance, trades, creative — no domain assumptions

### 🎯 Triple Matching Engine
| Mode | Speed | Privacy | Best For |
|------|-------|---------|----------|
| **TF-IDF** | ⚡ Fastest | 100% Local | Quick results, no ML |
| **BERT** | 🚀 Fast | 100% Local | Semantic matching, no API key |
| **Azure** | ☁️ Cloud | Sanitized only | Best accuracy (requires key) |
| **Hybrid** | 🎯 Balanced | Mixed | Production default |

### ⚡ Performance Optimization
- **Model Manager**: `@st.cache_resource` persists models across sessions
- **Warmup on Startup**: BERT loads once at app start (~15s), then instant
- **Graceful Fallbacks**: Azure → BERT → TF-IDF → spaCy (chain of availability)

### 📡 Multi-Source Aggregation
- 6+ remote job boards scraped in real-time
- Automated deduplication by title + company
- Keyword filtering with 30-result limit

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Framework** | Streamlit 1.28+ with `@st.cache_resource` model singleton |
| **LLM Extraction** | Azure OpenAI (gpt-4o-mini), **Structured Outputs** (Pydantic) |
| **Local AI** | sentence-transformers (BERT), spaCy NER fallback |
| **Matching** | **Semantic similarity scoring** via TF-IDF / BERT / Azure Embeddings |
| **PII Sanitization** | **PII tokenization** + **GDPR Article 17** immediate purge |
| **Parsing** | pdfplumber, python-docx with **magic bytes detection** |
| **Scraping** | requests, BeautifulSoup4, **concurrent.futures** parallel with timeout |
| **Deployment** | Hugging Face Spaces |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- (Optional) Azure OpenAI API Key for enhanced extraction

### 2. Installation
```bash
git clone https://github.com/YOUR_USERNAME/job-hunter-pro.git
cd job-hunter-pro
pip install -r requirements.txt
```

**Note**: First run downloads ~80MB BERT model (cached for future runs).

**HuggingFace Free Tier**: 
- Cold start: 20-30s on first load (2 vCPU, no GPU)
- Default TF-IDF mode recommended for speed
- BERT mode available but slower on CPU
- For best performance, run locally or upgrade to HuggingFace Pro

### 3. Running Locally
```bash
streamlit run app.py
```

App will show "Loading AI models (one-time)..." on first startup.

### 4. Configuration (Optional)
Create a `.env` file to enable Azure OpenAI features:
```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

**Without these**: App runs 100% locally using BERT + TF-IDF (no API calls).

---

## 📁 Architecture

```
JOB_HUNTER/
├── app.py                      # Streamlit entry point
├── requirements.txt            # Dependencies
├── src/
│   ├── parser.py              # Re-export (backward compat)
│   ├── parser_v2.py           # Dynamic LLM-based parser ⭐
│   ├── pii_sanitizer.py      # GDPR-compliant PII masking ⭐
│   ├── llm_extractor.py      # Azure OpenAI structured extraction ⭐
│   ├── matcher.py            # Re-export (backward compat)
│   ├── matcher_v2.py         # Dynamic matching (BERT/TF-IDF/Azure) ⭐
│   ├── model_manager.py      # Cached model loading ⭐
│   ├── scraper.py            # Multi-source job scraper
│   └── ui.py                 # Streamlit components
└── README.md
```

**⭐ = New in v2.0**

---

## 👨‍💻 Author

**Chukwuma Clifford Nwanna**  
*AI/ML Engineer | Azure AI Developer*  
[LinkedIn](https://linkedin.com/in/chukwumanwanna) | [GitHub](https://github.com/cliffordnwanna)

---

## 📄 License
MIT License - 2026 Chukwuma Clifford Nwanna
