from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Загрузка пользователей
def load_users():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# Сохранение пользователей
def save_users(users):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    query = request.args.get('q', '')
    users = load_users()
    vacancies = [user for user in users if user.get('role') == 'работодатель']
    if query:
        vacancies = [v for v in vacancies if query.lower() in v.get('location', '').lower()]
    return render_template('index.html', vacancies=vacancies)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        data = dict(request.form)
        data['photo'] = None

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                filename = secure_filename(photo.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(path)
                data['photo'] = filename

        users.append(data)
        save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        for user in users:
            if user['email'] == request.form['email'] and user['password'] == request.form['password']:
                session['user'] = user
                return redirect(url_for('profile'))
        return 'Неверные данные'
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session['user'])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
