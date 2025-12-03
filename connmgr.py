
import wifi
import adafruit_connection_manager
import adafruit_requests

radio = wifi.radio

# Add code to make sure your radio is connected

pool = adafruit_connection_manager.get_radio_socketpool(radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(radio)
requests = adafruit_requests.Session(pool, ssl_context)
requests.get("http://wifitest.adafruit.com/testwifi/index.html")

# Do something with response
