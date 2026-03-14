# # Remote-ACC

Remote-ACC é um aplicativo de acesso remoto que permite controlar um computador via navegador web. Ele captura a tela do host em tempo real e envia para clientes conectados, permitindo interações como cliques do mouse, digitação de texto e comandos especiais de teclado.

## Funcionalidades

- **Captura de tela em tempo real**: O servidor captura screenshots continuamente e os transmite via WebSocket para os clientes.
- **Controle remoto**: Clientes podem clicar na imagem da tela para simular cliques do mouse.
- **Digitação remota**: Permite enviar texto e comandos especiais de teclado (como Enter, Tab, Esc, etc.).
- **Ajuste de FPS**: Controle a taxa de quadros por segundo (0.1 a 5 FPS) para otimizar desempenho.
- **Autenticação**: Protegido por uma chave de 4 dígitos gerada aleatoriamente a cada inicialização.
- **Interface gráfica**: GUI em Tkinter para iniciar/parar o servidor, visualizar logs e acessar facilmente via QR code.
- **Interface web**: Frontend responsivo em HTML/CSS/JavaScript para controle via navegador.

## Tecnologias Utilizadas

- **Backend**: Flask com Flask-SocketIO para WebSockets.
- **Captura de tela**: PyAutoGUI e Pillow.
- **Frontend**: HTML, CSS, JavaScript com Socket.IO.
- **GUI**: Tkinter com QR code gerado via qrcode e PIL.
- **Empacotamento**: PyInstaller para criar executáveis standalone.

## Pré-requisitos

- Python 3.7 ou superior.
- Dependências listadas em `requirements.txt`.

## Instalação

1. Clone ou baixe o repositório.
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Como Executar

### Opção 1: Via GUI (Recomendado)

1. Execute o arquivo `gui.pyw`:
   ```
   python gui.pyw
   ```
2. Na interface gráfica:
   - Clique em "Iniciar Servidor".
   - Anote o IP exibido e a chave de autenticação.
   - Use o QR code para acessar rapidamente no dispositivo móvel ou escaneie com um app de QR code.

3. Abra um navegador e acesse o URL fornecido na interface (ex: `http://192.168.1.100:5000`).
4. Digite a chave de 4 dígitos quando solicitado.
5. Agora você pode controlar o computador remotamente.

### Opção 2: Via Linha de Comando

1. Execute o servidor diretamente:
   ```
   python app.py
   ```
2. Observe o console para a chave de autenticação e o IP.
3. Acesse via navegador como acima.

## Segurança

- A autenticação é básica (chave de 4 dígitos). Use em redes seguras.
- O servidor escuta em todas as interfaces (0.0.0.0). Restrinja o acesso se necessário.
- Não use para fins maliciosos; respeite a privacidade e leis locais.

## Limitações

- Requer Python no sistema para execução direta.
- Captura de tela pode ser intensiva em CPU/GPU.
- Não suporta múltiplos monitores nativamente (configurado para 1280x720).
- Sem criptografia avançada; use VPN para conexões remotas inseguras.

## Contribuição

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades. Abra issues ou pull requests no repositório.

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para detalhes.
