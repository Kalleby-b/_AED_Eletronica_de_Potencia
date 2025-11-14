import network
import socket
from machine import Pin, ADC
import time

# ======== CONFIGURAÇÕES ========
SSID = "SEU_SSID"
PASSWORD = "SUA_SENHA"

ADC_PIN = 32
adc = ADC(Pin(ADC_PIN))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

# ======== ESTADO DO SISTEMA ========
estado = {
    "ligado": False,
    "angulo": 0,
    "tensao": 0.0,
    "corrente": 0.0
}

# ======== HTML EMBUTIDO ========
pagina_html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Controle de Potência - ESP32</title>
<style>
body { font-family: Arial; text-align:center; background:#eef2f5; }
.card { background:#fff; margin:20px auto; width:320px; padding:20px; border-radius:10px;
        box-shadow:0 4px 10px rgba(0,0,0,0.1); }
button { padding:8px 14px; margin:8px; border:none; border-radius:6px; background:#007bff; color:#fff; font-size:15px; cursor:pointer; }
button:hover { background:#005fc7; }
input[type=number]{ width:70px; text-align:center; }
.value { font-size:22px; margin:6px 0; }
</style>
</head>
<body>
  <div class="card">
    <h2>Controle de Potência</h2>
    <div class="value">Tensão: <span id="tensao">--</span> V</div>
    <div class="value">Corrente: <span id="corrente">--</span> A</div>
    <div class="value">Ângulo: <span id="angulo">--</span>°</div>
    <div class="value">Sistema: <span id="estado">--</span></div>
    <div style="margin-top:10px;">
      <label>Novo Ângulo:</label>
      <input id="novoAngulo" type="number" min="0" max="180" step="1" value="0">
      <button onclick="enviarAngulo()">Enviar</button>
    </div>
    <div style="margin-top:10px;">
      <button onclick="alternar()">Ligar / Desligar</button>
      <button onclick="atualizar()">Atualizar</button>
    </div>
  </div>
<script>
function atualizar(){
  fetch('/estado').then(r=>r.json()).then(d=>{
    document.getElementById('tensao').innerText = d.tensao.toFixed(1);
    document.getElementById('corrente').innerText = d.corrente.toFixed(3);
    document.getElementById('angulo').innerText = d.angulo;
    document.getElementById('estado').innerText = d.ligado ? 'Ligado' : 'Desligado';
  });
}
function alternar(){
  fetch('/toggle').then(_=>atualizar());
}
function enviarAngulo(){
  const val = document.getElementById('novoAngulo').value;
  fetch('/set?angulo='+val).then(_=>atualizar());
}
setInterval(atualizar, 2000);
window.onload = atualizar;
</script>
</body>
</html>"""

# ======== FUNÇÕES AUXILIARES ========
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Conectando-se ao Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Conectado! IP:", wlan.ifconfig()[0])
    return wlan

def ler_adc():
    leitura = adc.read()
    v_adc = (leitura / 4095) * 3.3
    tensao = v_adc * 11     # ajuste conforme seu divisor resistivo
    corrente = v_adc * 100  # ajuste conforme sensor de corrente
    return tensao, corrente

# ======== SERVIDOR HTTP ========
def iniciar_servidor():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    print("Servidor web iniciado na porta 80")
    return s

# ======== LOOP PRINCIPAL ========
wlan = conectar_wifi()
server = iniciar_servidor()

while True:
    try:
        conn, addr = server.accept()
        req = conn.recv(1024).decode()
        caminho = req.split(' ')[1]

        # Atualiza leituras
        tensao, corrente = ler_adc()
        estado["tensao"] = tensao
        estado["corrente"] = corrente

        # ======= ROTAS =======
        if caminho == '/' or caminho == '/index.html':
            resposta = pagina_html
            conn.send('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
            conn.sendall(resposta)

        elif caminho.startswith('/estado'):
            resposta = '{{"tensao":{:.2f},"corrente":{:.3f},"angulo":{},"ligado":{}}}'.format(
                estado["tensao"], estado["corrente"], estado["angulo"], str(estado["ligado"]).lower())
            conn.send('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
            conn.sendall(resposta)

        elif caminho.startswith('/toggle'):
            estado["ligado"] = not estado["ligado"]
            print("Sistema ligado?" , estado["ligado"])
            conn.send('HTTP/1.0 200 OK\r\n\r\nOK')

        elif caminho.startswith('/set?'):
            try:
                partes = caminho.split('?')[1]
                for param in partes.split('&'):
                    if param.startswith('angulo='):
                        val = int(param.split('=')[1])
                        estado["angulo"] = max(0, min(180, val))
                        print("Novo ângulo:", estado["angulo"])
            except:
                pass
            conn.send('HTTP/1.0 200 OK\r\n\r\nOK')

        else:
            conn.send('HTTP/1.0 404 Not Found\r\n\r\nPágina não encontrada')

        conn.close()

    except Exception as e:
        print("Erro:", e)
