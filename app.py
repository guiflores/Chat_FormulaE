from flask import Flask, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO, join_room
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Configuração do Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Arquivo CSV para registrar os usuários
CSV_FILE = 'usuarios.csv'

# Armazenamento em memória para usuários
users = {}

# Modelo de Usuário
class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

# Função para carregar os pontos dos usuários
def carregar_pontos():
    if not os.path.exists(CSV_FILE):
        return {}
    
    pontos = {}
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            nome, email, pontos_usuario = row
            pontos[email] = {'nome': nome, 'pontos': int(pontos_usuario)}
    return pontos
def handle_watch_time(data):
    email = data['email']
    username = data['username']
    tempo_assistido = data['time']  # Tempo assistido enviado do frontend

    # Exemplo: Para cada 10 segundos assistidos, adicionamos 1 ponto
    incremento = tempo_assistido // 10  # Um ponto por 10 segundos assistidos
    pontos = atualizar_pontos(email, username, incremento=incremento)

# Função para salvar os pontos dos usuários
def salvar_pontos(pontos):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        for email, data in pontos.items():
            writer.writerow([data['nome'], email, data['pontos']])

# Função para atualizar os pontos do usuário
def atualizar_pontos(email, nome, incremento=0):
    pontos = carregar_pontos()
    if email in pontos:
        pontos[email]['pontos'] += incremento
    else:
        pontos[email] = {'nome': nome, 'pontos': incremento}
    
    salvar_pontos(pontos)
    return pontos[email]['pontos']


# Função para carregar usuários
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)


# Função para salvar usuários no CSV
def salvar_usuario(email, nome, pontos):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([email, nome, pontos, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

# Função para atualizar o usuário no CSV
def atualizar_usuario(email, nome, pontos):
    users_list = []
    # Lê os dados existentes
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == email:
                row[1] = nome
                row[2] = pontos
            users_list.append(row)
    
    # Salva os dados atualizados
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(users_list)

# Página de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Cria um novo usuário e adiciona ao dicionário
        user_id = str(len(users) + 1)  # ID incremental
        users[user_id] = User(user_id, email, hashed_password)

        return redirect(url_for('login'))
    return render_template('register.html')

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        for user in users.values():
            if user.email == email and check_password_hash(user.password, password):
                login_user(user)
                # Verifica se o usuário já tem um nome
                if not hasattr(user, 'username'):
                    return redirect(url_for('set_name'))
                return redirect(url_for('chat'))

        error = "Email ou senha incorretos."
        return render_template('login.html', error=error)

    return render_template('login.html')

# Colocar o nome
@app.route('/set_name', methods=['GET', 'POST'])
@login_required
def set_name():
    if request.method == 'POST':
        username = request.form['username']
        current_user.username = username
        current_user.points = 0  # Inicializa os pontos
        # Salvar no CSV
        salvar_usuario(current_user.email, username, current_user.points)
        return redirect(url_for('chat'))

    return render_template('set_name.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Página inicial com o chat
@app.route('/')
@login_required
def chat():
    return render_template('chat.html')

# Evento de conexão ao socket
@socketio.on('join')
def handle_join(data):
    username = data['username']
    email = data['email']
    room = data['room']
    join_room(room)
    pontos = atualizar_pontos(email, username)
    salvar_usuario(email, username, 0)  # Salvar nome e email do usuário
    socketio.emit('message', {'msg': f"{username} ({pontos} pontos) entrou no chat!"}, room=room)


# Evento de envio de mensagens
@socketio.on('message')
def handle_message(data):
    room = data['room']
    socketio.emit('message', {'msg': f"{data['username']}: {data['msg']}"}, room=room)

# Defina um valor para os pontos a serem ganhos e o tempo de visualização
POINTS_PER_INTERVAL = 15
VIEW_TIME_INTERVAL = 30  # Tempo em segundos

@app.route('/update_points', methods=['POST'])
@login_required
def update_points():
    current_user.points += POINTS_PER_INTERVAL
    # Atualizar no CSV
    atualizar_usuario(current_user.email, current_user.username, current_user.points)
    return {'points': current_user.points}

if __name__ == '__main__':
    socketio.run(app, debug=True)
