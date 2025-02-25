import machine
import time
import dht

led_green = machine.Pin(12, machine.Pin.OUT)
led_red = machine.Pin(13, machine.Pin.OUT)

d = dht.DHT11(machine.Pin(26))

def display_dht11():
    d.measure()
    temp = d.temperature()
    humid = d.humidity()
    print('Temperature	:', temp, '*C', '\nHumidity	:', humid, '%')
    return temp

def display_led(temp):
    temp_max = 34
    if temp >= temp_max:
        led_red.on()
        led_green.off()
    elif temp < temp_max:
        led_red.off()
        led_green.on()
    else:
        led_red.off()
        led_green.off()
        

interval = 2000
start = time.ticks_ms()

while True:
    if time.ticks_ms() - start >= interval:
        temp = display_dht11()
        display_led(temp)
        start = time.ticks_ms()
        print("LED Green	:", led_green.value())
        print("LED Red		:", led_red.value(), '\n')