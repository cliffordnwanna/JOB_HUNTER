# 🚀 Deploying to Hugging Face Spaces

This project is optimized for deployment to **Hugging Face Spaces** using the Streamlit SDK.

## Method 1: Direct Upload (Easiest)
1.  Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2.  Choose a name (e.g., `job-hunter-pro`).
3.  Select **Streamlit** as the SDK.
4.  Choose **Public** for portfolio visibility.
5.  Upload the following files/folders:
    - `app.py` (Main entry point)
    - `src/` (Folder with core logic)
    - `requirements.txt` (Dependencies)
    - `assets/` (If needed for images)

## Method 2: GitHub Sync (Professional / CI/CD)
1.  Create a new repository on GitHub.
2.  Push this project to the repository.
3.  Go to your Hugging Face Space settings.
4.  Enable **GitHub Sync**.
5.  Every time you push to GitHub, Hugging Face will automatically redeploy!

## 🔐 Configuring Secrets (For Azure OpenAI)
To enable the **Azure Semantic Matcher**:
1.  Go to your Space **Settings** -> **Variables and Secrets**.
2.  Add the following **Secrets**:
    - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI Key.
    - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI Endpoint.
    - `AZURE_OPENAI_DEPLOYMENT`: `text-embedding-3-small` (default).

## 🧩 Dependencies
Hugging Face will automatically install dependencies from `requirements.txt`. Ensure the file is at the root.
