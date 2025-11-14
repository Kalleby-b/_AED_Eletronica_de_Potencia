import paho.mqtt.client as mqtt

#broker = 'broker.hivemq.com'
broker = 'test.mosquitto.org'
port = 1883
topic = 'casa/sala/led'

client = mqtt.Client('cliente_pc')

client.connect(broker, port)

mensagem = 'OFF'
client.publish(topic, mensagem)

print(f'Mensagem "{mensagem}" enviada ao tópico "{topic}"')

client.disconnect()
