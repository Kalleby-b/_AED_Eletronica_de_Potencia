import network
import socket
import ujson
from machine import Pin, DAC

# === Configurações do Wi-Fi ===
SSID = "Alencar Oi 2.4G"
PASSWORD = "Carloshenrique"

# === Inicializa DAC no pino 25 ===
dac = DAC(Pin(25))
output_value = 0

# === Inicializa Wi-Fi ===
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, PASSWORD)

while not sta.isconnected():
    pass

print("Conectado à rede!")
print("Endereço IP:", sta.ifconfig()[0])

# === Função HTML inicial ===
def html_page():
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <meta name='ngrok-skip-browser-warning' content='true'>
    <title>Controle de Frequência e Vazão</title>
    <link rel="icon" href="data:,">
    <style>
        .container {
            width: 40%;
            margin: auto;
            padding: 20px;
            border: 2px solid #000;
            border-radius: 10px;
            background-color: #e0f7fa;
            text-align: center;
            font-family: Arial, sans-serif;
        }
        input[type=range] {
            width: 100%;
        }
        p {
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Controle do Inversor</h2>
        <input type="range" id="dacSlider" min="0" max="255" value="0" oninput="sendDAC(this.value)">
        <p>Valor DAC: <span id="dacVal">0</span></p>
        <p>Frequência: <strong><span id="freq">0.0</span> Hz</strong></p>
        <p>Vazão: <strong><span id="vazao">0.0</span> LPM</strong></p>
    </div>
    <script>
        function sendDAC(val) {
            document.getElementById('dacVal').innerText = val;
            fetch('/update?dac=' + val)
            .then(response => response.json())
            .then(data => {
                document.getElementById('freq').innerText = data.freq.toFixed(1);
                document.getElementById('vazao').innerText = data.vazao.toFixed(1);
            });
        }
    </script>
</body>
</html>"""
    return html

# === Criação do servidor ===
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)
print("Servidor iniciado!")

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode("utf-8")
        print("Requisição:", request)

        if "/favicon.ico" in request:
            conn.close()
            continue

        if "GET /update?dac=" in request:
            try:
                param = request.split("GET /update?dac=")[1].split(" ")[0]
                output_value = int(param)
                output_value = max(0, min(255, output_value))
                dac.write(output_value)
                print("DAC atualizado para:", output_value)
            except:
                print("Erro ao interpretar valor do DAC.")

            freq = (output_value / 255) * 60
            vazao = (output_value / 255) * 38
            data = {"freq": freq, "vazao": vazao}

            response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n"
            response += ujson.dumps(data)
            conn.sendall(response.encode("utf-8"))
            conn.close()
            continue

        # Página HTML inicial
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n"
            "\r\n"
            + html_page()
        )
        conn.sendall(response.encode("utf-8"))
        conn.close()

    except Exception as e:
        print("Erro:", e)
        conn.close()
