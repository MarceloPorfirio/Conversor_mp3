import os
import threading
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'url' not in request.form:
            flash('No URL provided')
            return redirect(request.url)
        
        url = request.form['url']
        try:
            youtube = YouTube(url)
        except:
            flash('Invalid YouTube URL')
            return redirect(request.url)

        video = youtube.streams.get_highest_resolution()
        filename = secure_filename(youtube.title + '.mp4')
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.download(output_path=app.config['UPLOAD_FOLDER'], filename=filename)

        mp3_filename = os.path.splitext(filename)[0] + '.mp3'
        mp3_filepath = os.path.join(app.config['UPLOAD_FOLDER'], mp3_filename)

        ffmpeg_thread = threading.Thread(target=convert_video_to_mp3, args=(temp_filepath, mp3_filepath))
        ffmpeg_thread.start()

        flash('Conversion started, please wait...')
        return redirect(url_for('index'))

    return render_template('index.html')

def convert_video_to_mp3(temp_filepath, mp3_filepath):
    ffmpeg_extract_audio(temp_filepath, mp3_filepath)
    os.remove(temp_filepath)  # Remove o arquivo de vídeo temporário após a conversão

@app.route('/check_status')
def check_status():
    # Simular verificação de status (retorne 100% para simular a conclusão da conversão)
    return jsonify({'percent': 100})

if __name__ == '__main__':
    app.run(debug=True)
