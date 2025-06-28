
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw
import os
import io
import zipfile
from datetime import datetime

app = Flask(__name__)
IMAGE_DIR = 'static/generated'
os.makedirs(IMAGE_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']
    # Simulate image generation with PIL
    img = Image.new('RGB', (512, 512), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), prompt, fill=(255, 255, 0))

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'image_{timestamp}.png'
    filepath = os.path.join(IMAGE_DIR, filename)
    img.save(filepath)

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
    port = int(os.environ.get('PORT', 5000))  # Render provides PORT env var
    app.run(host='0.0.0.0', port=port, debug=True)

