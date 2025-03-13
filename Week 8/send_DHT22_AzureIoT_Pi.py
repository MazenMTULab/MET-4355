import os
import asyncio
import time
import uuid
import sys
import adafruit_dht  # Use the CircuitPython DHT library
import board  # Board library to access GPIO pins
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

# Pin where the DHT22 sensor is connected (change this as needed)
DHT_PIN = board.D4  # GPIO Pin to which the DHT22 is connected
sensor = adafruit_dht.DHT22(DHT_PIN)  # DHT22 sensor type

async def read_temp_humidity():
    try:
        # Reading data from DHT22 sensor
        humidity = sensor.humidity
        temperature = sensor.temperature
       
        if humidity is not None and temperature is not None:
            return round(temperature, 1), round(humidity, 1)
        else:
            print("Failed to read from the sensor. Retrying...")
            return None, None
    except Exception as e:
        print(f"Error reading from DHT22 sensor: {e}")
        return None, None

async def send_recurring_telemetry(device_client):
    # Connect the client.
    await device_client.connect()

    # Send recurring telemetry
    while True:
        temperature, humidity = await read_temp_humidity()
        if temperature is not None and humidity is not None:
            msg_txt_formatted = '{{"temperature": {temperature}, "humidity": {humidity}}}'
            data = msg_txt_formatted.format(temperature=temperature, humidity=humidity)
            msg = Message(data)
            msg.content_encoding = "utf-8"
            msg.content_type = "application/json"
            print("sending message - " + str(data))
            await device_client.send_message(msg)
        else:
            print("No valid data to send. Retrying...")

        time.sleep(3)

def main():
    # The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
    conn_str = "HostName=ThermostatIoTHub.azure-devices.net;DeviceId=AmnaRaspberryPi;SharedAccessKey=agKNjaY81aelq76ASlPySNXaxia83i0/ubqoLEgbSBk="
    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    print("IoTHub Device Client Recurring Telemetry Sample")
    print("Press Ctrl+C to exit")
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(send_recurring_telemetry(device_client))
    except KeyboardInterrupt:
        print("User initiated exit")
    except Exception:
        print("Unexpected exception!")
        raise
    finally:
        loop.run_until_complete(device_client.shutdown())
        loop.close()

if __name__ == "__main__":
    main()
