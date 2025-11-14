import network
import time
from umqtt.simple import MQTTClient
from machine import Pin, PWM

# === CONFIGURAÇÕES DO USUÁRIO ===
SSID = 'Alencar Oi 2.4G'
SENHA = 'Carloshenrique'
BROKER = 'test.mosquitto.org'
TOPICO = b'esp32/pwm'

# === CONFIGURAÇÃO DO PWM ===
pwm = PWM(Pin(5), freq=1000)
pwm.duty(0)

# === FUNÇÃO PARA CONVERTER VALOR PARA DUTY (0–1023) ===
def pwm_duty(valor):
    duty = int((valor / 120) * 1023)
    return min(max(duty, 0), 1023)

# === CONEXÃO WI-FI ===
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, SENHA)

while not wifi.isconnected():
    print("Conectando ao Wi-Fi...")
    time.sleep(1)

print("Conectado ao Wi-Fi:", wifi.ifconfig())

# === CALLBACK DO MQTT ===
def tratar_mensagem(topico, msg):
    try:
        valor_pwm = int(msg)
        duty = pwm_duty(valor_pwm)
        pwm.duty(duty)
        print(f"Recebido: {valor_pwm} → Duty: {duty}")
    except Exception as e:
        print("Erro ao interpretar valor:", e)

# === CONEXÃO COM BROKER MQTT ===
cliente = MQTTClient("esp32", BROKER, port=1883)
cliente.set_callback(tratar_mensagem)
cliente.connect()
cliente.subscribe(TOPICO)
print(f"Conectado ao broker MQTT '{BROKER}', aguardando dados no tópico '{TOPICO.decode()}'")

# === LOOP PRINCIPAL ===
try:
    while True:
        cliente.check_msg()
        time.sleep(0.1)
except KeyboardInterrupt:
    cliente.disconnect()
    print("Desconectado do broker")
