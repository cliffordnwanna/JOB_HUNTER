#!/bin/bash
# Pre-download ML models at build time to avoid runtime delay
# Hugging Face Spaces runs this during container build
# IMPORTANT: This file must be executable (chmod +x setup.sh)

echo "🤖 Pre-downloading BERT model for faster cold starts..."
python3 -c "
from sentence_transformers import SentenceTransformer
print('Downloading all-MiniLM-L6-v2...')
model = SentenceTransformer('all-MiniLM-L6-v2')
print('✅ BERT model cached successfully')
"

echo "🧠 Pre-downloading spaCy model for NER fallback..."
python3 -m spacy download en_core_web_sm

echo "📦 Setup complete!"
