# Chat em Tempo Real com Flask e Socket.IO

Este é um projeto de chat em tempo real construído com **Flask** e **Socket.IO**, com autenticação de usuário e persistência de dados em um arquivo CSV. As senhas são armazenadas de forma segura com **bcrypt**.

## Funcionalidades

- Autenticação de usuário
  - Login de usuários com senha criptografada (bcrypt)
  - Registro automático de novos usuários com armazenamento de senha hashada
- Chat em tempo real
  - Comunicação em tempo real entre os usuários
  - Conexão a diferentes salas de chat
- Persistência de dados
  - Usuários e senhas são salvos em um arquivo CSV (`usuarios_senhas.csv`)

## Pré-requisitos

Antes de executar o projeto, certifique-se de ter o Python e as seguintes bibliotecas instaladas:

- Flask
- Flask-SocketIO
- bcrypt

Você pode instalar as dependências necessárias usando o seguinte comando:

```bash
pip install Flask Flask-SocketIO bcrypt
```

## Segurança
-As senhas são armazenadas de forma segura utilizando o bcrypt. 
-As sessões de usuário são protegidas usando uma chave secreta definida no SECRET_KEY da aplicação Flask.
