const socket = io();
const img = document.getElementById("stream");
let authenticated = false;
let preloader = new window.Image();
function solicitarChave() {
    let chave = prompt("Digite a chave de 4 dígitos fornecida pelo servidor:");
    if (chave) {
        socket.emit("auth", { key: chave });
    }
}

socket.on("auth_required", () => {
    solicitarChave();
});

socket.on("auth_ok", () => {
    authenticated = true;
    alert("Autenticado com sucesso!");
});

socket.on("auth_fail", () => {
    alert("Chave incorreta. Tente novamente.");
    solicitarChave();
});

socket.on("frame", data => {
    if (!authenticated) return;
    preloader.onload = () => {
        img.src = preloader.src;
    };
    preloader.src = "data:image/jpeg;base64," + data.image;
});

img.addEventListener("click", e => {
    if (!authenticated) return;
    const rect = img.getBoundingClientRect();
    const x = (e.clientX - rect.left) / img.clientWidth;
    const y = (e.clientY - rect.top) / img.clientHeight;
    socket.emit("click", { relX: x, relY: y });
});

function enviarTexto() {
    if (!authenticated) return;
    const texto = document.getElementById("texto").value.trim();
    if (texto) socket.emit("digitar", { texto });
}

function enviarComando(key) {
    if (!authenticated) return;
    socket.emit('special_key', { key });
}

function ajustarFPS() {
    if (!authenticated) return;
    const valor = parseFloat(document.getElementById("fps").value);
    if (valor >= 0.1 && valor <= 5) {
        socket.emit("set_fps", { fps: valor });
    } else {
        alert("FPS inválido (0.1 - 5)");
    }
}

function encerrarServidor() {
    if (!authenticated) return;
    if (confirm("Deseja encerrar o servidor?")) {
        socket.emit("encerrar");
        console.log("Servidor encerrado");
    }
}
