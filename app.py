from flask import Flask, render_template, request, send_file
import os
import requests
import io
import zipfile
from datetime import datetime
from PIL import Image

app = Flask(__name__)
IMAGE_DIR = 'static/generated'
os.makedirs(IMAGE_DIR, exist_ok=True)

HF_TOKEN = os.getenv('HF_TOKEN')
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
print("Using token:", HF_TOKEN[:6], "..." if HF_TOKEN else "No token found")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    payload = {
        "inputs": prompt
    }

    response = requests.post(HF_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return f"Error generating image: {response.text}", 500

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"image_{timestamp}.png"
    filepath = os.path.join(IMAGE_DIR, filename)

    with open(filepath, 'wb') as f:
        f.write(response.content)

    image_url = filepath.replace("static/", "")
    return render_template('result.html', image_url=image_url, prompt=prompt)

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