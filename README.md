# yt-downloader

אפליקציית Flask להורדת וידאו או אודיו מיוטיוב באמצעות yt-dlp.

## הרצה מקומית

```bash
pip install -r requirements.txt
python app.py        # http://localhost:5000
```

## פריסה (Render)

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300`
- **Health check:** `/healthz`

## עוגיות (אופציונלי)

אם יוטיוב חוסם הורדות, אפשר לספק קובץ עוגיות בפורמט Netscape.
הנתיב נקבע במשתנה הסביבה `COOKIES_FILE` (ברירת מחדל: `cookies.txt` ליד `app.py`).
**אין לשמור את הקובץ ב-git** – הוא מכיל פרטי התחברות. הוא נמצא ב-`.gitignore`.

## התנהגות

- מקבל רק קישורי YouTube.
- כל הורדה נשמרת בתיקייה זמנית משלה ונמחקת אחרי 15 דקות.
- ל-FFmpeg אין תלות: אין מיזוג או המרה, הפורמט נבחר כפי שיוטיוב מספק.
