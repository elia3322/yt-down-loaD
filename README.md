# yt-downloader Flask App

This is a simple Flask web application that allows you to download YouTube videos or audio using yt-dlp.

## 🚀 Deploy to Render

1. Create a free account at [https://render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository containing this project
4. Set the following settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Environment:** Python 3
5. Make sure your folder structure includes:
   - `app.py`
   - `templates/index.html`
   - `static/style.css`
   - `downloads/` (empty folder for storing downloaded files)
   - `requirements.txt`
   - `Procfile`
6. Optionally include `cookies.txt` if you use authenticated downloads.

After deployment, your app will be accessible via a public URL provided by Render.
