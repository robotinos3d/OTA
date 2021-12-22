#------------------------------------------------------------------
# main.py
#------------------------------------------------------------------

############################# IMPORT #############################

import uasyncio as asyncio
import machine
import time
import utime
import json

from app.current.mqtt_as import MQTTClient, config
from app.current.PrinterController import PrinterController
from app.current.config import Config
from app.current import mqtt
from app.current.token import Token

####################### OBJETS INSTANCES #########################

manager_config = Config()

######################## GLOBAL VARIABLES ########################

tupleblish = None
timeout_to_send_payload = manager_config.load_config('app_config')['timeout_to_send_payload']

######################## GLOBAL CONSTANTS #########################

CLIENT_ID = manager_config.load_config('wifi_config')['MAC_address'] #La constante del archivo mqtt tiene el mismo valor
IP = manager_config.load_config('mqtt_config')['server']
    
############################## MAIN ##############################

def start_main():     

    # ------------------- SUBSCRIPTION CALLBACK -------------------

    def sub_cb(topic, msg, retained):
        global tupleblish    
        tupleblish = mqtt_message_handler.process_message(topic,msg)

    # ------------ DEMOSTRATE SCHEDULES IS OPERATIONAL ------------
    
    async def heartbeat():
        s = True
        status_led = machine.Pin(14, machine.Pin.OUT)
        while True:
            await asyncio.sleep_ms(1000)
            status_led.on()
            await asyncio.sleep_ms(1000)
            status_led.off()
            s = not s

    async def wifi_han(state):
        print('Wifi is ', 'up' if state else 'down')
        await asyncio.sleep(1)

    # -------------------- SUBSCRIBE TO TOPICS --------------------

    async def conn_han(client):
        await client.subscribe(mqtt.SUB_TOPIC_CONFIG_CAMERA, 1)
        await client.subscribe(mqtt.SUB_TOPIC_CONFIG_JSON, 1)
        await client.subscribe(mqtt.SUB_TOPIC_COMMAND_MARLIN, 1)
        await client.subscribe(mqtt.SUB_TOPIC_COMMAND_ESP, 1)
        await client.subscribe(mqtt.SUB_TOPIC_ECHO, 1)

    # ---------------------------- MAIN ----------------------------

    async def main(client):
        global tupleblish
        global timeout_to_send_payload

        # ------------------------- TIME STAMP -------------------------

        start = utime.time()
        
        # ---------------------- OBJETS INSTANCES ----------------------

        printer_contrl = PrinterController()
        button = machine.Pin(2, machine.Pin.IN)

        # --------------------- CONNECT TO SERVER ----------------------

        try:
            await client.connect()
        except OSError:
            print('>>> Connection failed. Resetting machine...')
            time.sleep(5)
            machine.reset()
            return

        # ----------------------- SINGLE SHIPMENT ----------------------

        printer_contrl.get_stats()
        printer_contrl.get_information()
        printer_contrl.print_on_screen('Impresora conectada al servidor')

        try:
            with open('/app/.version') as version_file:
                version = version_file.readline()
                await client.publish(mqtt.PUB_TOPIC_DATA, 'version:{}'.format(version), qos = 1)
        except:
            print("Problem to open version file")

        # ---------------------------- LOOP ----------------------------

        while True:

            if mqtt_message_handler.updated_send_payload_timeout == True:
                timeout_to_send_payload = manager_config.load_config('app_config')['timeout_to_send_payload']
                mqtt_message_handler.updated_send_payload_timeout = False

            # --------------------------- UART PROCESS --------------------------
            
            try:
                uart_message = printer_contrl.process_uart()
            except:
                uart_message = ''
                print('>>> Error al leer la UART')

            # ---------------------------- SEND TOKEN ---------------------------

            if uart_message and 'generate_token' in uart_message:
                token_generator = Token()
                token = token_generator.generate_token()
                await client.publish(mqtt.PUB_TOPIC_TOKEN, "{}:{}".format(CLIENT_ID, str(token)), qos = 1)
                printer_contrl.print_on_screen('Token: {}'.format(token))
                
            if mqtt_message_handler.working:

                # ------------------------ SEND UART MESSAGE -----------------------
                
                if uart_message:
                    await client.publish(mqtt.PUB_TOPIC_ACK_MARLIN, uart_message, qos = 1)

                # ------------------ ASSEMBLE PAYLOAD AND SEND IT ------------------

                if (utime.time() - start >= timeout_to_send_payload):
                    printer_contrl.get_temp()
                    printer_contrl.get_pos()
                    printer_contrl.get_sd_status()
                    payload = printer_contrl.get_payload()
                    await client.publish(mqtt.PUB_TOPIC_DATA, payload , qos = 1)
                    start = utime.time()

                # ------------------------- SEND TUPLEBLISH -------------------------

                if tupleblish != None:    
                    await client.publish(topic = tupleblish[0],  msg = tupleblish[1],  retain = False,  qos= 1)
                    tupleblish = None
                    print(">>> PUBLISHED")

            await asyncio.sleep_ms(100)
            

    mqtt_message_handler = mqtt.MQTTMessageHandler()

    # ----------------------- DEFINE CONFIGURATION -----------------------

    config['subs_cb'] = sub_cb
    config['wifi_coro'] = wifi_han
    config['connect_coro'] = conn_han
    config['clean'] = True
    config['client_id'] = CLIENT_ID
    config['server'] = IP
    config['ssid'] = ''     # Will look for it into Network_FSM.py machine state
    config['wifi_pw'] = ''   

    # --------------------------- SET UP CLIENT ---------------------------

    MQTTClient.DEBUG = True  
    client = MQTTClient(config)

    loop = asyncio.get_event_loop()
    loop.create_task(heartbeat())

    try:
        loop.run_until_complete(main(client))
    finally:
        client.close()  # Prevent LmacRxBlk:1 errors
