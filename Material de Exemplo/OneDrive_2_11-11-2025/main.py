from machine import Pin
import network
import time
from umqtt.simple import MQTTClient

# 📶 Configuração da Wi-Fi
ssid = 'Alencar Oi 2.4G'
password = 'Carloshenrique'

# 🔌 Conectando ao Wi-Fi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid, password)

print('Conectando-se ao Wi-Fi...')
while not sta_if.isconnected():
    time.sleep(1)
print('Wi-Fi conectado:', sta_if.ifconfig())

# 💡 Configuração do LED (agora no GPIO5)
led = Pin(5, Pin.OUT)

# 📨 Configuração do MQTT
#broker = 'broker.hivemq.com'
broker = 'test.mosquitto.org'
client_id = 'esp32_led_controller'
topic_sub = b'casa/sala/led'

def callback_mqtt(topic, msg):
    print('Mensagem recebida:', topic, msg)
    if msg == b'ON':
        led.on()
    elif msg == b'OFF':
        led.off()

client = MQTTClient(client_id, broker)
client.set_callback(callback_mqtt)
client.connect()
client.subscribe(topic_sub)

print('Aguardando mensagens no tópico', topic_sub)

try:
    while True:
        client.check_msg()
        time.sleep(1)
except KeyboardInterrupt:
    client.disconnect()
    print('Desconectado do MQTT')
