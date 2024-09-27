from flask import Flask, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, join_room
from flask_cors import CORS
import csv
import os
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Arquivo CSV para registrar os usuários e senhas
USERS_FILE = 'usuarios_senhas.csv'

# Função para carregar os usuários
def carregar_usuarios():
    if not os.path.exists(USERS_FILE):
        return {}
    
    usuarios = {}
    with open(USERS_FILE, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            nome, senha_hash = row
            usuarios[nome] = senha_hash
    return usuarios

# Função para salvar um novo usuário
def salvar_usuario(nome, senha_hash):
    with open(USERS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nome, senha_hash])

# Rota de login via API
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    nome = data['nome']
    senha = data['senha']

    usuarios = carregar_usuarios()

    if nome in usuarios:
        senha_hash = usuarios[nome].encode('utf-8')
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
            session['nome'] = nome
            return jsonify({'status': 'success', 'nome': nome}), 200
        else:
            return jsonify({'status': 'failed', 'message': 'Senha incorreta!'}), 401
    else:
        # Se o usuário for novo, cadastrar e salvar a senha hashada
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        salvar_usuario(nome, senha_hash.decode('utf-8'))
        session['nome'] = nome
        return jsonify({'status': 'success', 'nome': nome}), 200

# Evento de conexão ao socket
@socketio.on('join')
def handle_join(data):
    nome = data['nome']
    room = data['room']
    join_room(room)
    socketio.emit('message', {'msg': f"{nome} entrou no chat!"}, room=room)

# Evento de envio de mensagens
@socketio.on('message')
def handle_message(data):
    room = data['room']
    nome = data['nome']
    socketio.emit('message', {'msg': f"{nome}: {data['msg']}"}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
