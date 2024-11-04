from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.secret_key = 'auth'
app.config['MONGO_URI'] = "mongodb+srv://auth:auth@auth.e7xuu.mongodb.net/auth?retryWrites=true&w=majority"
mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, username, user_type):    
        self.username = username
        self.user_type = user_type
        
    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(username):
    user_data = mongo.db.users.find_one({"username": username})
    if user_data:
        return User(username=user_data['username'], user_type=user_data['user_type'])
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("Reached the register route")  # Log para verificar se a rota é atingida
    if request.method == 'POST':
        print("Processing registration form")  # Log para verificar se o formulário foi enviado
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        matricula = request.form.get('matricula')  # Obtém a matrícula se existir
        existing_user = mongo.db.users.find_one({"username": username})

        if existing_user:
            flash('Username already exists.')
        else:
            user_data = {
                "username": username,
                "password": password,  # Considere usar hash em produção
                "user_type": user_type
            }

            if user_type == 'student' and matricula:
                user_data["matricula"] = matricula  # Adiciona a matrícula ao registro

            try:
                mongo.db.users.insert_one(user_data)
                flash('Registration successful! Please log in.')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'An error occurred: {e}')  # Mostra erro se algo der errado

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = mongo.db.users.find_one({"username": username, "password": password})

        if user_data:
            user = User(username=user_data['username'], user_type=user_data['user_type'])
            login_user(user)
            return redirect(url_for('dashboard'))

        flash('Login Failed. Check your credentials.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'student':
        # Exibe apenas as atividades do aluno logado
        activities = mongo.db.activities.find({"student": current_user.username})
    elif current_user.user_type == 'teacher':
        # Exibe apenas as atividades atribuídas ao professor logado
        activities = mongo.db.activities.find({"teacher": current_user.username})
    else:
        activities = []

    return render_template('dashboard.html', activities=activities)


@app.route('/add_activity', methods=['POST'])
@login_required
def add_activity():
    data = request.get_json()
    activity_name = data['name']
    status = data['status']
    teacher = data['teacher']
    student_email = data.get('studentEmail', current_user.username)

    # Adiciona a nova atividade ao banco de dados
    mongo.db.activities.insert_one({
        "name": activity_name,
        "status": status,
        "teacher": teacher,
        "student": student_email,
    })
    return jsonify({"status": "success", "message": "Activity added."}), 200


@app.route('/save_activities', methods=['POST'])
@login_required
def save_activities():
    print("save_activities called")
    data = request.get_json()
    print("Received data:", data)  # Log para verificar o que está sendo recebido

    activities = data.get("activities")
    print("Parsed activities:", activities)  # Log para verificar as atividades

    # Limpa as atividades atuais do usuário antes de salvar as novas
    mongo.db.activities.delete_many({"student": current_user.username})

    if activities:
        for activity in activities:
            print("Saving activity:", activity)  # Log para verificar cada atividade
            mongo.db.activities.insert_one({
                "name": activity['name'],
                "status": activity['status'],
                "teacher": activity['teacher'],
                "student": current_user.username  # Garante que a atividade seja salva com o nome do usuário
            })

    return jsonify({"status": "success", "message": "Activities saved."}), 200


@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
