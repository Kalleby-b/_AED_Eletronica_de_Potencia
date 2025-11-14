import network
import socket
import time
from machine import Pin
import dht

# === Configurações do Wi-Fi ===
SSID = "Nome_do_Hotspot"
PASSWORD = "Senha"

# === Inicializa sensor DHT11 no pino 15 ===
sensor = dht.DHT11(Pin(15))

# === Inicializa Wi-Fi ===
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, PASSWORD)

while not sta.isconnected():
    pass

print("Conectado à rede!")
print("Endereço IP:", sta.ifconfig()[0])

# === Função HTML com os dados atualizados ===
def webpage(temp, hum):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>DHT11 - Temperatura e Umidade</title>
    <meta http-equiv=\"refresh\" content=\"5\">
    <meta name=\"ngrok-skip-browser-warning\" content=\"true\">
    <style>
        .container {{
            width: 30%;
            margin: auto;
            padding: 20px;
            border: 2px solid #000;
            border-radius: 10px;
            background-color: #f0f0f0;
            text-align: center;
            font-family: Arial, sans-serif;
        }}
        h2 {{
            margin-bottom: 20px;
        }}
        p {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h2>Leitura do DHT11</h2>
        <p>Temperatura: <strong>{temp} &deg;C</strong></p>
        <p>Umidade: <strong>{hum} %</strong></p>
    </div>
</body>
</html>"""
    return html

# === Criação do servidor socket ===
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)
print("Servidor iniciado!")

while True:
    try:
        conn, addr = s.accept()
        print("Conexão de", addr)

        # Lê dados do DHT11
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        # Gera a resposta HTTP completa de uma vez
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n"
            "ngrok-skip-browser-warning: true\r\n"
            "\r\n"
            + webpage(temp, hum)
        )

        # Recebe a requisição (limpa o buffer)
        conn.recv(1024)
        # Envia toda a resposta de uma vez como bytes
        conn.sendall(response.encode("utf-8"))
        conn.close()

    except OSError as e:
        print("Erro:", e)
        conn.close()
