HOST       = "localhost"
PORT       = 4223
DB_USER    = 'sensor_input'
DB_PW      = 'j"%!R^9UMX2~_6?A'
PUBLIC_IP  = '52.41.56.54'
STATION_ID = "0"

# Object holders
ambient_light = None
barometer     = None
thermometer   = None
humidity      = None

# Holders for most recent readings
last_ambient_light_reading = None
last_barometer_reading     = None
last_thermometer_reading   = None
last_humidity_reading      = None

# 1 minute chosen for testing purposes
callback_response = 60

# Import bindings
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bicklet_ambient_light_v2 import BrickletAmbientLightV2
from tinkerforge.bicklet_barometer import BrickletBarometer
from tinkerforge.bicklet_temperature import BrickletTemperature
from tinkerforge.bicklet_humidity import BrickletHumidity
import mysql.connector
import time

# Callback functions
def al_cb(illum):
    global last_ambient_light_reading
    last_ambient_light_reading = illum

def al_thr_cb(illum):
    pass

def b_cb(press):
    global last_barometer_reading
    last_barometer_reading = press

def b_thr_cb(press):
    pass

def th_cb(temp):
    global last_thermometer_reading
    last_thermometer_reading = temp

def th_thr_cb(temp):
    pass

def h_cb(hum):
    global last_humidity_reading
    last_humidity_reading = hum

def h_thr_cb(hum):
    pass

if __name__ == "__main__":
    ipcon = IPConnection()
    ipcon.connect(HOST, PORT)

    # Connect with the MySQL Server
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PW, host=PUBLIC_IP, database='test')
    cursor = cnx.cursor()
    add_row = ("INSERT INTO test_table "
               "(Sensor_ID, ambient_light_reading, barometer_reading, thermometer_reading, humidity_reading, send_time) "
               "VALUES (%s, %s, %s, %s, %s)")

    # Create bricklet objects
    ambient_light = BrickletAmbientLightV2()
    barometer     = BrickletBarometer()
    thermometer   = BrickletTemperature()
    humidity      = BrickletHumidity()

    # Set debounce periods
    ambient_light.set_debounce_period(1000)
    barometer.set_debounce_period(1000)
    thermometer.set_debounce_period(1000)
    humidity.set_debounce_period(1000)

    # Set callback periods
    ambient_light.set_ambient_light_callback_period(60000)
    barometer.set_air_pressure_callback_period(60000)
    thermometer.set_temperature_callback_period(60000)
    humidity.set_humidity_callback_period(60000)

    # Register callbacks
    ambient_light.register_callback(ambient_light.CALLBACK_ILLUMINANCE, al_cb)
    barometer.register_callback(barometer.CALLBACK_AIR_PRESSURE, b_cb)
    thermometer.register_callback(thermometer.CALLBACK_TEMPERATURE, th_cb)
    humidity.register_callback(humidity.CALLBACK_HUMIDITY, h_cb)
    
    # Register threshold callbacks
    ambient_light.register_callback(ambient_light.CALLBACK_ILLUMINANCE_REACHED, al_thr_cb)
    barometer.register_callback(barometer.CALLBACK_AIR_PRESSURE_REACHED, b_thr_cb)
    thermometer.register_callback(thermometer.CALLBACK_TEMPERATURE_REACHED, th_thr_cb)
    humidity.register_callback(humidity.CALLBACK_HUMIDITY_REACHED, h_thr_cb)

    
    start_time = time.time()
    try:
        while True:
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            data = (STATION_ID, last_ambient_light_reading, last_barometer_reading, last_thermometer_reading,
                    last_humidity_reading, now)
            cursor.execute(add_row, data)
            time.sleep(callback_response - ((time.time() - start_time) % callback_response))
    except KeyboardInterrupt:
        pass

    print "Disconnecting"
    ipcon.disconnect()
    cursor.close()
    cnx.close()
