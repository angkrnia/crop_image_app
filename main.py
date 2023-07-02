import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.secret_key = 'un!v3r51t@sP4mulAn9'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def crop_image(image, size, position):
    width, height = image.size

    positions = {
        'top_left': (0, 0, size, size),
        'top_center': ((width - size) // 2, 0, (width + size) // 2, size),
        'top_right': (width - size, 0, width, size),
        'center_left': (0, (height - size) // 2, size, (height + size) // 2),
        'center': ((width - size) // 2, (height - size) // 2, (width + size) // 2, (height + size) // 2),
        'center_right': (width - size, (height - size) // 2, width, (height + size) // 2),
        'bottom_left': (0, height - size, size, height),
        'bottom_center': ((width - size) // 2, height - size, (width + size) // 2, height),
        'bottom_right': (width - size, height - size, width, height)
    }

    if position in positions:
        left, upper, right, lower = positions[position]
        cropped_image = image.crop((left, upper, right, lower))
        return cropped_image

    return None

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
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            file.save(file_path)
            return redirect(url_for('crop_image_route', filename=filename))
        else:
            flash('Invalid file format')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/crop/<filename>', methods=['GET', 'POST'])
def crop_image_route(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(file_path)

    if request.method == 'POST':
        size = int(request.form['size'])
        if size > image.width or size > image.height:
            flash('Crop size is larger than image size')
            return redirect(request.url)

        position = request.form['position']
        cropped_image = crop_image(image, size, position)

        if cropped_image:
            cropped_filename = f"cropped_{filename}"
            cropped_file_path = os.path.join(app.config['UPLOAD_FOLDER'], cropped_filename)
            cropped_image.save(cropped_file_path)
            return redirect(url_for('show_cropped', filename=cropped_filename))
        else:
            flash('Invalid crop position')
            return redirect(request.url)

    return render_template('crop.html', filename=filename, image_width=image.width, image_height=image.height)

@app.route('/cropped/<filename>')
def show_cropped(filename):
    cropped_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template('cropped.html', filename=filename, cropped_file_path=cropped_file_path)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
