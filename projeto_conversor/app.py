import os
import threading

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
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
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
            mp3_filepath = os.path.join(app.config['UPLOAD_FOLDER'], mp3_filename)

            ffmpeg_thread = threading.Thread(target=convert_video_to_mp3, args=(temp_filepath, mp3_filepath))
            ffmpeg_thread.start()

            flash('Conversion started, please wait...')
            return redirect(url_for('index'))

    return render_template('index.html')

def convert_video_to_mp3(temp_filepath, mp3_filepath):
    ffmpeg_extract_audio(temp_filepath, mp3_filepath)

@app.route('/check_status', methods=['GET'])
def check_status():
    # Implementar a verificação de status da conversão aqui
    # Retornar o status como um JSON
    status = {
        "percent": 100  # Altere para o valor real do progresso
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True)
