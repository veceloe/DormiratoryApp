from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Данные о стиральных машинах
machines = [
    {"id": 1, "status": "Available", "time_remaining": 0, "queue": []},
    {"id": 2, "status": "Busy", "time_remaining": 30, "queue": []},
    {"id": 3, "status": "Available", "time_remaining": 0, "queue": []},
    {"id": 4, "status": "Busy", "time_remaining": 45, "queue": []},
    {"id": 5, "status": "Available", "time_remaining": 0, "queue": []},
]

# Пример данных профиля пользователя
user_profile = {
    "floor": "3",
    "room": "305",
    "block": "A",
    "hobbies": "Чтение, спорт",
    "about": "Студент МГУ",
    "photo": None  # URL или путь к фотографии
}

# Путь к папке для сохранения изображений
IMAGES_FOLDER = os.path.join('static', 'images')
os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Путь к CSV-файлу для хранения объявлений
ADVERTS_CSV = 'adverts.csv'

# Создание CSV-файла, если он не существует
if not os.path.exists(ADVERTS_CSV):
    df = pd.DataFrame(columns=['title', 'date', 'username', 'image', 'price', 'type', 'block', 'room'])
    df.to_csv(ADVERTS_CSV, index=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['user'] = request.form['username']
        return redirect(url_for('index'))

    if 'user' not in session:
        return render_template('set_username.html')

    return render_template('index.html', machines=machines, user=session['user'])


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_profile['floor'] = request.form['floor']
        user_profile['room'] = request.form['room']
        user_profile['block'] = request.form['block']
        user_profile['hobbies'] = request.form['hobbies']
        user_profile['about'] = request.form['about']
        # Здесь можно добавить логику для загрузки и сохранения фотографии
        return redirect(url_for('profile'))

    return render_template('profile.html', user=session['user'], profile=user_profile)


@app.route('/market', methods=['GET'])
def market():
    if 'user' not in session:
        return redirect(url_for('index'))

    df = pd.read_csv(ADVERTS_CSV)
    adverts = df.to_dict(orient='records')

    return render_template('market.html', user=session['user'], adverts=adverts)


@app.route('/create_advert', methods=['GET', 'POST'])
def create_advert():
    if 'user' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        date = datetime.now().strftime("%Y-%m-%d")
        image = request.files['image']
        price = request.form['price']
        type = request.form['type']
        username = session['user']
        block = user_profile['block']
        room = user_profile['room']

        # Сохранение изображения
        image_path = os.path.join(IMAGES_FOLDER, image.filename)
        image.save(image_path)

        # Сохранение данных в CSV
        df = pd.read_csv(ADVERTS_CSV)
        new_advert = pd.DataFrame([{'title': title, 'date': date, 'username': username, 'image': image_path,
                                    'price': price, 'type': type, 'block': block, 'room': room}])
        df = pd.concat([df, new_advert], ignore_index=True)
        df.to_csv(ADVERTS_CSV, index=False)

        return redirect(url_for('market'))

    return render_template('create_advert.html')


@app.route('/join_queue/<int:machine_id>', methods=['POST'])
def join_queue(machine_id):
    user = session.get('user')
    if user:
        for machine in machines:
            if machine['id'] == machine_id and user not in machine['queue']:
                machine['queue'].append(user)
                break
    return redirect(url_for('index'))


@app.route('/leave_queue/<int:machine_id>', methods=['POST'])
def leave_queue(machine_id):
    user = session.get('user')
    if user:
        for machine in machines:
            if machine['id'] == machine_id and user in machine['queue']:
                machine['queue'].remove(user)
                break
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
