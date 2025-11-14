import network
import socket
from machine import Pin

# ============================
# CONFIGURAÇÕES DE REDE
# ============================
SSID = 'Alencar Oi 2.4G'         # Substitua pelo nome da sua rede Wi-Fi
SENHA = 'Carloshenrique'       # Substitua pela senha do seu Wi-Fi

# Conecta ao Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, SENHA)

print("Conectando ao Wi-Fi...")
while not wifi.isconnected():
    pass

print("Conectado com sucesso!")
ip_local = wifi.ifconfig()[0]
print("Endereço IP:", ip_local)

# ============================
# CONFIGURAÇÃO DO LED
# ============================
led = Pin(5, Pin.OUT)

# ============================
# FUNÇÃO HTML DA PÁGINA
# ============================
def pagina_html():
    estado = "Ligado" if led.value() else "Desligado"
    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Controle de LED</title>
</head>
<body style="font-family:sans-serif; text-align:center; padding-top:50px;">
    <h1>Controle do LED (GPIO 5)</h1>
    <h2>Estado atual: <strong>{estado}</strong></h2>
    <a href="/ligar"><button style="font-size:24px; padding:10px;">LIGAR</button></a>
    <a href="/desligar"><button style="font-size:24px; padding:10px;">DESLIGAR</button></a>
</body>
</html>"""
    return html

# ============================
# SERVIDOR WEB
# ============================
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(('', 80))
servidor.listen(1)

print("\nServidor web iniciado!")
print("Acesse no navegador ou pelo Node-RED:")
print(f"http://{ip_local}/ligar")
print(f"http://{ip_local}/desligar")

while True:
    conexao, endereco = servidor.accept()
    print("Cliente conectado:", endereco)
    requisicao = conexao.recv(1024).decode()
    print("Requisição recebida:", requisicao)

    if 'GET /ligar' in requisicao:
        led.on()
    elif 'GET /desligar' in requisicao:
        led.off()

    resposta = pagina_html()

    # Cabeçalhos HTTP com UTF-8 corretamente especificado
    conexao.send('HTTP/1.1 200 OK\r\n')
    conexao.send('Content-Type: text/html; charset=utf-8\r\n')
    conexao.send('Connection: close\r\n\r\n')
    conexao.sendall(resposta)
    conexao.close()
