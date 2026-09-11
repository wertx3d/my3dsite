import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ПРАВИЛЬНЫЙ ПУТЬ ДЛЯ ХОСТИНГА: создаем базу в разрешенной папке /tmp
db_path = os.path.join('/tmp', 'models.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Папка для загрузки 3D-моделей
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'models')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Модель базы данных для хранения информации о файлах
class Model3D(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)

# Главная страница, где выводятся все модельки
@app.route('/')
def index():
    models = Model3D.query.all()
    return render_template('index.html', models=models)

# Маршрут для загрузки новой 3D-модели через форму
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    model_name = request.form.get('name')
    
    if file and file.filename != '' and model_name:
        filename = file.filename
        # Проверяем, существует ли папка для сохранения файлов, если нет — создаем ее
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Сохраняем информацию в базу данных
        new_model = Model3D(name=model_name, filename=filename)
        db.session.add(new_model)
        db.session.commit()
        
    return redirect(url_for('index'))

# Автоматически создаем базу данных перед обработкой первого запроса, если её ещё нет
@app.before_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    # Этот блок нужен для локального запуска (python app.py)
    app.run(debug=True)
