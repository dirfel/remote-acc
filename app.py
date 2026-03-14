from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from PIL import Image
from io import BytesIO
import threading
import time
import pyautogui
import base64
import os
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
limite_tentativas = 5
tentativas = {}
fps = 2  # valor inicial
largura, altura = 1280, 720  # Resolução padrão para captura de tela

AUTH_KEY = f"{random.randint(0000, 9999):04d}"  # Chave de autenticação aleatória
print(f"Chave de autenticação: {AUTH_KEY}")

# Mapeia session_id para autenticação
authenticated_clients = set()

@app.route('/')
def index():
    return render_template('index.html')

def capturar_e_enviar():
    global fps, largura, altura
    while True:
        try:
            for sid in list(authenticated_clients):
                try:
                    screenshot = pyautogui.screenshot().resize((largura, altura))
                    buffer = BytesIO()
                    screenshot.save(buffer, format="JPEG", quality=50)
                    img_base64 = base64.b64encode(buffer.getvalue()).decode()
                    socketio.emit('frame', {'image': img_base64}, to=sid)
                except Exception as e:
                    print("Erro ao capturar/enviar:", e)
        except Exception as e:
            print("Erro ao capturar/enviar:", e)
        time.sleep(1 / fps if fps > 0 else 1)

@socketio.on('connect')
def on_connect():
    emit('auth_required')

@socketio.on('auth')
def on_auth(data):
    key = data.get('key', '')
    sid = request.sid
    tentativas.setdefault(sid, 0)
    if tentativas[sid] >= limite_tentativas:
        emit('auth_fail', {'error': 'Limite de tentativas excedido.'})
        return False
    if key == AUTH_KEY:
        authenticated_clients.add(request.sid)
        tentativas.pop(sid, None)  # Limpa tentativas se autenticado
        emit('auth_ok')
    else:
        tentativas[sid] += 1
        emit('auth_fail')
        if tentativas[sid] >= limite_tentativas:
            return False
        return False  # Desconecta

def require_auth(func):
    def wrapper(*args, **kwargs):
        if request.sid not in authenticated_clients:
            emit('auth_required')
            return
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@socketio.on('click')
@require_auth
def receber_click(data):
    relX = data['relX']
    relY = data['relY']
    screen_w, screen_h = pyautogui.size()
    x = int(relX * screen_w)
    y = int(relY * screen_h)
    pyautogui.click(x, y)

@socketio.on('digitar')
@require_auth
def digitar(data):
    texto = data['texto']
    pyautogui.write(texto, interval=0.05)

@socketio.on('special_key')
@require_auth
def special_key(data):
    key = data.get('key')
    if key in ['ctrl', 'alt', 'shift', 'esc', 'tab', 'home', 'end', 'pageup', 'pagedown']:
        pyautogui.press(key)

@socketio.on('set_fps')
@require_auth
def set_fps(data):
    global fps
    try:
        valor = float(data.get('fps', 5))
        if 0.1 <= valor <= 5:
            fps = valor
            print(f"FPS ajustado para {fps}")
    except:
        print("FPS inválido recebido.")

@socketio.on('encerrar')
@require_auth
def encerrar():
    print("Encerrando servidor.")
    os._exit(0)

@socketio.on('disconnect')
def on_disconnect():
    authenticated_clients.discard(request.sid)
    tentativas.pop(request.sid, None)

if __name__ == '__main__':
    threading.Thread(target=capturar_e_enviar, daemon=True).start()
    socketio.run(app, 
                 host='0.0.0.0', 
                #  host='::', 
                 port=5000, 
                 debug=False, 
                 use_reloader=False,
                 log_output=False
                 )
