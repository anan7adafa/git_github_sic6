import machine
import time
import dht
import network
import ujson
from umqtt.simple import MQTTClient

# Konfigurasi WiFi
WIFI_SSID = "Kost ema eksklusif"
WIFI_PASSWORD = "gejayan251124"

# Konfigurasi MQTT Ubidots
UBIDOTS_TOKEN = "BBUS-4pUpT4sQBMvJp5af2jgMydwHOm0OzH"
UBIDOTS_BROKER = "industrial.api.ubidots.com"
UBIDOTS_CLIENT_ID = "ESP32_Ubidots"
UBIDOTS_PORT = 1883
UBIDOTS_TOPIC_PUB = "/v1.6/devices/esp32_dht11"
UBIDOTS_TOPIC_SUB_RED = "/v1.6/devices/esp32_dht11/led_red/lv"
UBIDOTS_TOPIC_SUB_GREEN = "/v1.6/devices/esp32_dht11/led_green/lv"
UBIDOTS_TOPIC_PUB_PIR = "/v1.6/devices/esp32_dht11/PIR"

# Konfigurasi MQTTX (Broker EMQX)
MQTTX_BROKER = "broker.emqx.io"
MQTTX_CLIENT_ID = "ESP32_MQTTX"
MQTTX_PORT = 1883
MQTTX_TOPIC_PUB = "iot/dht11"
MQTTX_TOPIC_CONTROL = "iot/control"

# Inisialisasi perangkat
led_red = machine.Pin(13, machine.Pin.OUT)
led_green = machine.Pin(12, machine.Pin.OUT)
dht_sensor = dht.DHT11(machine.Pin(26))
pir_sensor = machine.Pin(27, machine.Pin.IN)  # Pin untuk sensor PIR

# Fungsi untuk koneksi WiFi
def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    
    print("Menghubungkan ke WiFi...")
    while not wifi.isconnected():
        time.sleep(1)
    print("WiFi Terhubung:", wifi.ifconfig())

# Fungsi callback saat menerima data dari MQTT
def on_message(topic, message):
    topic = topic.decode()
    message = message.decode()
    print("Pesan diterima:", topic, message)

    if topic == MQTTX_TOPIC_CONTROL:
        if message == "red_on":
            led_red.value(1)
        elif message == "red_off":
            led_red.value(0)
        elif message == "green_on":
            led_green.value(1)
        elif message == "green_off":
            led_green.value(0)

    if topic == UBIDOTS_TOPIC_SUB_RED:
        try:
            if float(message) == 1.0:
                led_red.value(1)
            elif float(message) == 0.0:
                led_red.value(0)
        except ValueError:
            print("Error: Format pesan tidak valid untuk LED merah.")

    if topic == UBIDOTS_TOPIC_SUB_GREEN:
        try:
            if float(message) == 1.0:
                led_green.value(1)
            elif float(message) == 0.0:
                led_green.value(0)
        except ValueError:
            print("Error: Format pesan tidak valid untuk LED hijau.")

# Fungsi untuk mengirim data ke Ubidots & MQTTX
def publish_data():
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    pir_status = pir_sensor.value()  # Membaca status PIR (1 = terdeteksi, 0 = tidak terdeteksi)
    
    data_ubidots = ujson.dumps({
        "temperature": temperature,
        "humidity": humidity,
        "PIR": pir_status  # Menambahkan status PIR
    })
    
    data_mqttx = ujson.dumps({
        "temp": temperature,
        "humid": humidity
    })

    print("Mengirim data ke Ubidots:", data_ubidots)
    mqtt_ubidots.publish(UBIDOTS_TOPIC_PUB, data_ubidots)
    mqtt_ubidots.publish(UBIDOTS_TOPIC_PUB_PIR, str(pir_status))  # Mengirim status PIR secara terpisah

    print("Mengirim data ke MQTTX:", data_mqttx)
    mqtt_mqttx.publish(MQTTX_TOPIC_PUB, data_mqttx) 

# Koneksi WiFi
connect_wifi()

# Koneksi ke MQTT Ubidots
mqtt_ubidots = MQTTClient(UBIDOTS_CLIENT_ID, UBIDOTS_BROKER, port=UBIDOTS_PORT, user=UBIDOTS_TOKEN, password="", keepalive=60)
mqtt_ubidots.set_callback(on_message)
mqtt_ubidots.connect()
mqtt_ubidots.subscribe(UBIDOTS_TOPIC_SUB_RED)
mqtt_ubidots.subscribe(UBIDOTS_TOPIC_SUB_GREEN)
print("Terhubung ke Ubidots MQTT!")

# Koneksi ke MQTTX
mqtt_mqttx = MQTTClient(MQTTX_CLIENT_ID, MQTTX_BROKER, port=MQTTX_PORT, keepalive=60)
mqtt_mqttx.set_callback(on_message)
mqtt_mqttx.connect()
mqtt_mqttx.subscribe(MQTTX_TOPIC_CONTROL)
print("Terhubung ke MQTTX!")

# Loop utama
while True:
    mqtt_ubidots.check_msg()
    mqtt_mqttx.check_msg()
    publish_data()  # Kirim data sensor ke Ubidots & MQTTX
    time.sleep(5)

