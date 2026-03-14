import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import subprocess
import socket
import sys
import os
import re
import webbrowser
import qrcode
from PIL import Image, ImageTk

APP_FILE = "app.py"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class ConsoleRedirect:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, msg):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')

    def flush(self):
        pass

class RemoteAccGUI:
    def __init__(self, master):
        self.master = master
        master.title("Remote-ACC Backend GUI")
        master.geometry("800x540")

        # Frame principal horizontal
        main_frame = tk.Frame(master)
        main_frame.pack(fill="x", padx=5, pady=8)

        # Frame dos campos (lado esquerdo)
        fields_frame = tk.Frame(main_frame)
        fields_frame.pack(side="left", fill="both", expand=True)

        # Status do servidor
        status_frame = tk.Frame(fields_frame, bd=2, relief="groove")
        status_frame.pack(fill="x", pady=(0, 8))
        self.status_rect = tk.Frame(status_frame, width=30, height=30, bg="#cccc00")
        self.status_rect.pack(side="left", padx=8, pady=4)
        self.status_label = tk.Label(status_frame, text="Desativado", font=("Consolas", 12, "bold"))
        self.status_label.pack(side="left", padx=8)
        self.set_status("desativado")

        # IP
        tk.Label(fields_frame, text="IP para acesso:").pack(anchor="w")
        self.ip_entry = tk.Entry(fields_frame, font=("Consolas", 12), state="readonly", cursor="hand2")
        self.ip_entry.pack(fill="x")
        self.ip_entry.bind("<Button-1>", self.abrir_url)

        # Código de autenticação
        tk.Label(fields_frame, text="Código de autenticação:").pack(anchor="w", pady=(8, 0))
        self.code_entry = tk.Entry(fields_frame, font=("Consolas", 12), state="readonly")
        self.code_entry.pack(fill="x")
        self.set_code("----")

        # Frame do QR Code (lado direito)
        qr_frame = tk.Frame(main_frame)
        qr_frame.pack(side="left", padx=40, pady=4, anchor="n")
        self.qr_label = tk.Label(qr_frame)
        self.qr_label.pack(expand=True)

        # Inicializa IP e QR
        self.set_ip(get_local_ip())

        # # Código
        # tk.Label(master, text="Código de autenticação:").pack(anchor="w")
        # self.code_entry = tk.Entry(master, font=("Consolas", 12), state="readonly")
        # self.code_entry.pack(fill="x", padx=5)
        # self.set_code("----")

        # Logs
        tk.Label(master, text="Logs do servidor:").pack(anchor="w")
        self.log_box = ScrolledText(master, height=8, font=("Consolas", 10), state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        

        # Botões
        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=5)
        self.start_btn = tk.Button(btn_frame, text="Iniciar Servidor", command=self.start_server, bg="green", fg="white")
        self.start_btn.pack(side="left", padx=10)
        self.stop_btn = tk.Button(btn_frame, text="Encerrar Servidor", command=self.stop_server, bg="red", fg="white", state="disabled")
        self.stop_btn.pack(side="left", padx=10)

        self.proc = None
        self.log_thread = None
        ad_frame = tk.Frame(master, bd=2, relief="sunken", bg="#222")
        ad_frame.pack(fill="x", padx=5, pady=8, side="bottom")
        ad_label = tk.Label(
            ad_frame,
            text="Desenvolvido por Dirfel - github.com/dirfel",
            font=("Consolas", 10, "italic"),
            fg="#fff",
            bg="#222",
            cursor="hand2"
        )
        ad_label.pack(padx=8, pady=6)
        ad_label.bind("<Button-1>", lambda e: os.system('start https://github.com/dirfel'))

        self.proc = None
        self.log_thread = None

    def abrir_url(self, event):
        url = self.ip_entry.get()
        webbrowser.open(url)

    def set_status(self, status):
        # status: "erro", "desativado", "executando", "inicializando", "encerrando"
        colors = {
            "desativado": "#d32f2f",     # vermelho
            "erro": "#cccc00",           # amarelo
            "executando": "#388e3c",     # verde
            "inicializando": "#1976d2",  # azul
            "encerrando": "#1976d2",     # azul
        }
        labels = {
            "erro": "Erro",
            "desativado": "Desativado",
            "executando": "Executando",
            "inicializando": "Inicializando...",
            "encerrando": "Encerrando...",
        }
        color = colors.get(status, "#cccccc")
        label = labels.get(status, status.capitalize())
        self.status_rect.config(bg=color)
        self.status_label.config(text=label)

    def set_ip(self, ip):
        url = f"http://{ip}:5000"
        self.ip_entry.config(state="normal")
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, url)
        self.ip_entry.config(state="readonly")
        # Gerar QR Code maior
        qr_img = qrcode.make(url)
        qr_img = qr_img.resize((120, 120), Image.LANCZOS)  # Aumente o tamanho aqui
        self.qr_photo = ImageTk.PhotoImage(qr_img)
        self.qr_label.config(image=self.qr_photo)

    def set_code(self, code):
        self.code_entry.config(state="normal")
        self.code_entry.delete(0, tk.END)
        self.code_entry.insert(0, code)
        self.code_entry.config(state="readonly")

    def start_server(self):
        if self.proc is not None:
            return
        self.set_status("inicializando")
        self.log_box.configure(state="normal")
        self.log_box.delete(1.0, tk.END)
        self.log_box.configure(state="disabled")
        try:
            self.proc = subprocess.Popen(
                [sys.executable, APP_FILE],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.log_thread = threading.Thread(target=self.read_logs, daemon=True)
            self.log_thread.start()
        except Exception as e:
            self.set_status("erro")
            self.append_log(f"Erro ao iniciar servidor: {e}\n")

    def stop_server(self):
        if self.proc:
            self.set_status("encerrando")
            try:
                self.proc.terminate()
            except Exception:
                pass
            self.proc = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.set_status("desativado")

    def append_log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, msg)
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    def read_logs(self):
        code_pattern = re.compile(r"Chave de autenticação: (\d{4})")
        erro_detectado = False
        while self.proc and self.proc.poll() is None:
            line = self.proc.stdout.readline()
            if not line:
                break
            self.append_log(line)
            if "Chave de autenticação" in line:
                self.set_status("executando")
            if "Traceback" in line or "Erro" in line:
                self.set_status("erro")
                erro_detectado = True
            match = code_pattern.search(line)
            if match:
                self.set_code(match.group(1))
        self.proc = None
        if not erro_detectado:
            self.set_status("desativado")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteAccGUI(root)
    root.mainloop()