
from flask import Flask, render_template, request, send_file
import os
import requests
import io
import zipfile
from datetime import datetime
from base64 import b64decode

app = Flask(__name__)
IMAGE_DIR = 'static/generated'
os.makedirs(IMAGE_DIR, exist_ok=True)

STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
STABILITY_API_URL = 'https://api.stability.ai/v1/generation/stable-diffusion-v1-5/text-to-image'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']

    headers = {
        'Authorization': f'Bearer {STABILITY_API_KEY}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    json_data = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30
    }

    response = requests.post(STABILITY_API_URL, headers=headers, json=json_data)

    if response.status_code != 200:
        return f"Error generating image: {response.text}", 500

    image_data = response.json()['artifacts'][0]['base64']
    image_bytes = b64decode(image_data)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'image_{timestamp}.png'
    filepath = os.path.join(IMAGE_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(image_bytes)

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
