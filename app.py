
from flask import Flask, render_template, request, send_file
import os
import requests
import io
import zipfile
from datetime import datetime

app = Flask(__name__)
IMAGE_DIR = 'static/generated'
os.makedirs(IMAGE_DIR, exist_ok=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_URL = 'https://api.openai.com/v1/images/generations'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "prompt": prompt,
        "n": 1,
        "size": "512x512"
    }

    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    if response.status_code != 200:
        return f"Error generating image: {response.text}", 500

    image_url = response.json()['data'][0]['url']
    image_data = requests.get(image_url).content

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'image_{timestamp}.png'
    filepath = os.path.join(IMAGE_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(image_data)

    return render_template('result.html', image_url=filepath, prompt=prompt)

@app.route('/download/<filename>')
def download(filename):
    image_path = os.path.join(IMAGE_DIR, filename)
    prompt_text = f"Prompt used for generation: {filename}\n"

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(image_path, arcname=filename)
        zip_file.writestr('prompt.txt', prompt_text)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='image_package.zip')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
