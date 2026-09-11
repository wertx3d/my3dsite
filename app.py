import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# База данных в разрешенной папке /tmp
db_path = os.path.join('/tmp', 'models.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Папка для загрузки 3D-моделей
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'models')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

class Model3D(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    models = Model3D.query.all()
    return render_template('index.html', models=models)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    model_name = request.form.get('name')
    
    if file and file.filename != '' and model_name:
        filename = file.filename
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_model = Model3D(name=model_name, filename=filename)
        db.session.add(new_model)
        db.session.commit()
        
    return redirect(url_for('index'))

@app.before_request
def create_tables():
    db.create_all()

# Этот блок теперь сработает и на хостинге SpaceWeb
if __name__ == '__main__':
    # Слушаем на порту 5000 на всех адресах, как требует хостинг
    app.run(host='0.0.0.0', port=5000)
