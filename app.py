from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string, flash, \
    render_template, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_MIME_TYPES = [
    'image/jpeg',
    'image/png',
    'application/pdf',
    'application/msword',
    'application/vnd.ms-excel',
    'application/vnd.ms-powerpoint',
    'text/plain'
]


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {'gabi': {'password': generate_password_hash('gabi')}}

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username]['password'], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('upload_form'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def upload_form():
    files = os.listdir(UPLOAD_FOLDER)
    file_links = [url_for('download_file', name=file) for file in files]
    return render_template('home.html', files=zip(files, file_links))


@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    mime_type = file.content_type
    if mime_type not in ALLOWED_MIME_TYPES:
        flash('File type is not allowed')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        flash('File successfully uploaded')
        return redirect(url_for('upload_form'))
    else:
        flash('Allowed file types are: {}'.format(", ".join(ALLOWED_MIME_TYPES)))
        return redirect(request.url)

@app.route('/delete/<name>')
def delete_file(name):
    file_path = os.path.join(UPLOAD_FOLDER, name)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('upload_form'))

@app.route('/file-list')
def file_list():
    files = os.listdir(UPLOAD_FOLDER)
    file_links = {file: url_for('download_file', name=file) for file in files}
    return jsonify(file_links)


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(UPLOAD_FOLDER, name)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)