from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from yt_dlp import YoutubeDL

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# יצירת תיקיית הורדות אם לא קיימת
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# הגדרות כלליות
COMMON_YDL_OPTIONS = {
    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
    'noplaylist': True,
    'quiet': True,
    'no_check_certificate': True,
    'socket_timeout': 340,
    'cookies': 'cookies.txt'
}

def download_video(url: str) -> str:
    ydl_opts = COMMON_YDL_OPTIONS.copy()
    ydl_opts['format'] = 'best'  # ללא מיזוג
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def download_audio(url: str) -> str:
    ydl_opts = COMMON_YDL_OPTIONS.copy()
    ydl_opts['format'] = 'bestaudio/best'  # ללא המרה ל-MP3
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        format_choice = request.form['format']
        try:
            if format_choice == 'audio':
                file_path = download_audio(url)
            else:
                file_path = download_video(url)
            filename = os.path.basename(file_path)
            return redirect(url_for('download_file', filename=filename))
        except Exception as e:
            return f"שגיאה בהורדה: {e}"
    return render_template('index.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
