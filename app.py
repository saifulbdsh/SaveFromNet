import yt_dlp
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info', methods=['POST'])
def get_info():
    video_url = request.form.get('url')
    if not video_url:
        # English Error Message
        return render_template('index.html', error="Please provide a video link.")

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            
            formats = info_dict.get('formats', [])
            video_formats = []
            audio_formats = []

            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    filesize = f.get('filesize')
                    video_formats.append({
                        'resolution': f.get('format_note', 'N/A'),
                        'ext': f.get('ext'),
                        'filesize_mb': round(filesize / (1024 * 1024), 2) if filesize else 'N/A',
                        'url': f.get('url'),
                    })
            
            for f in formats:
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('abr'):
                    filesize = f.get('filesize')
                    audio_formats.append({
                        'abr': f.get('abr', 0),
                        'ext': f.get('ext'),
                        'filesize_mb': round(filesize / (1024 * 1024), 2) if filesize else 'N/A',
                        'url': f.get('url'),
                    })

            audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
            
            return render_template('download.html',
                                   title=info_dict.get('title'),
                                   thumbnail=info_dict.get('thumbnail'),
                                   video_formats=video_formats,
                                   audio_formats=audio_formats)

    except Exception as e:
        # English Error Message
        error_message = f"An error occurred. Please check the link or try another one."
        return render_template('index.html', error=error_message)

if __name__ == '__main__':
    app.run(debug=True)