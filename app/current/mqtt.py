#------------------------------------------------------------------
# boot_logger.py
#------------------------------------------------------------------

############################# IMPORT #############################

import network
import time
import machine
import json

from app.current.config import Config
from app.current.PrinterController import PrinterController
from app.current.CamController import CamController
from id_manager import get_id

########################### JSON CONFIG ###########################

UUID = get_id()

########################## TOPIC DIAGRAM ##########################

#* ____'UUID' ____ /config_camera (S)
#*  |          |              
#*  |          |__ /config_json (S) 
#*  |          |              
#*  |          |__ /command ____ /marlin (S)          
#*  |          |             | 
#*  |          |             |__ /esp (S)
#*  |          |
#*  |          |__ /echo (S)
#*  |          |
#?  |          |__ /data (P)
#?  |          |
#?  |          |__ /ack ____ /marlin (P)
#?  |                    |            
#?  |                    |__ /esp (P)
#?  |                    |
#?  |                    |__ /photo (P) 
#?  |                          
#?  |__ /token (P)

########################## PUBLISH TOPICS ##########################

PUB_TOPIC_DATA = UUID + '/data_4_1_3'
PUB_TOPIC_ACK_MARLIN = UUID + '/ack/marlin'  
PUB_TOPIC_ACK_ESP = UUID + '/ack/esp'  
PUB_TOPIC_ACK_PHOTO = UUID + '/ack/photo'  
PUB_TOPIC_TOKEN = 'token' 

######################### SUBSCRIBED TOPICS #########################

SUB_TOPIC_CONFIG_CAMERA = UUID + '/config_camera'         
SUB_TOPIC_CONFIG_JSON = UUID + '/config_json'
SUB_TOPIC_COMMAND_MARLIN = UUID + '/command/marlin'
SUB_TOPIC_COMMAND_ESP = UUID + '/command/esp'
SUB_TOPIC_ECHO = UUID + '/echo'

################# MESSAGES FROM SUBSCRIBED TOPICS ###################

# SUB_TOPIC_CONFIG_CAMERA:
MSG_CAM_FRAMESIZE = 'cam_framesize'
MSG_CAM_FLIP = 'cam_flip'
MSG_CAM_MIRROR = 'cam_mirror'
MSG_CAM_WHITEBALANCE = 'cam_whitebalance'
MSG_CAM_SATURATION = 'cam_saturation'
MSG_CAM_BRIGHTNESS = 'cam_brightness'
MSG_CAM_CONTRAST = 'cam_contrast'
MSG_CAM_QUALITY = 'cam_quality'

# SUB_TOPIC_COMMAND_ESP:
MSG_CAM_SHOT = 'cam_shot'
MSG_RESET = 'reset' 
MSG_SLEEP = 'sleep'
MSG_WORK = 'work'
MSG_VERSION = 'version'

######################### MQTTMessageHandler ########################

class MQTTMessageHandler:
    """
    Esta clase maneja todos los mensajes recibidos por MQTT.
    Dependiendo del topico por le cual se hayan recibido, diferentes funciones procesaran su contenido.
    """

    def __init__(self):
        """
        Este constructor, inicializa las camara, la UART y designa que funcion procesara cada topico.
        """

        self.topics_handlers = {
            SUB_TOPIC_CONFIG_CAMERA:   self.config_camera,
            SUB_TOPIC_CONFIG_JSON:     self.config_json, 
            SUB_TOPIC_COMMAND_MARLIN:  self.command_marlin,
            SUB_TOPIC_COMMAND_ESP:     self.command_esp,
            SUB_TOPIC_ECHO:            self.echo_message,
        }

        self.printerController =   PrinterController()
        self.camController =       CamController()
        self.config =              Config()

        self.updated_send_payload_timeout = False
        self.working = True

    # -------------------- SUB_TOPIC_CONFIG_CAMERA --------------------

    def config_camera(self, message):
        """
        Recibe <message> que contiene un parametro y un valor, correspondiente a la configuracion de la camara, y lo setea.
        Luego devuelve una confirmacion por el topico <PUB_TOPIC_ACK_ESP>.

        Args:
            message (str): Cadena de texto con el parametro y el valor, separados por un '='. (ejemplo: 'cam_saturation=1')

        Returns:
            (tuple): Tupla con el topico por donde se debe responder y la respuesta
        """

        print(">>> Handling topic cam settings: " + message)
        self.camController.apply_setting(message)
        tupleblish = (PUB_TOPIC_ACK_ESP, b'camera settings success' )

        return tupleblish

    # --------------------- SUB_TOPIC_CONFIG_JSON ---------------------

    def config_json(self, message):
        """
        Recibe <message> con una clave <key> y un valor <value> implicitos, y actualiza el valor de dicha clave
        en el archivo .json.

        Args:
            message (str): String con el formato <key>-<value>, donde <key> es una de las claves de segundo orden
            del archivo config.json, y <value> es el valor que queremos setear en dicha clave.
        """

        key, value = message.split("-")
        
        print("update config_json: {key}:{value}".format(
            key = key,
            value = value))

        if value.isdigit():
            value = int(value)

        if key == 'timeout_to_send_payload':
            self.updated_send_payload_timeout = True

        self.config.save_config(key, value)

    # -------------------- SUB_TOPIC_COMMAND_MARLIN --------------------

    def command_marlin(self, message):
        """
        Recibe un gcode y lo envia a traves de la UART.

        Args:
            message (str): Gcode para enviar

        Returns:
            (tuple): Tupla vacia
        """

        print("commands: " + message)
        self.printerController.send_command(message)

        return 

    # ---------------------- SUB_TOPIC_COMMAND_ESP ---------------------

    def command_esp(self, message):
        """
        Recibe <message> y dependiendo del contenido realiza las siguientes tareas:

        - Si <message> contiene <MSG_CAM_SHOT>: Toma una fotografia y devuelve una tupla con el topico <PUB_TOPIC_ACK_PHOTO>
        y la fotografia en binario.

        - Si <message> contiene <MSG_RESET>: reinicia el ESP.

        - Si <message> contiene <MSG_SLEEP>: ...

        - Si <message> contiene <MSG_WORK>: ...

        - Si <message> contiene <MSG_VERSION>: Devuelve una tupla con el topico <PUB_TOPIC_DATA> y la version del firware del ESP.

        Args:
            message (str): String que contiene alguno de los siguientes: <MSG_CAM_SHOT> / <MSG_RESET> / <MSG_SLEEP> / <MSG_WORK>

        Returns:
            (tuple): Tupla con el topico por donde se debe responder y la respuesta. (En el caso de que haya respuesta)
        """

        if MSG_CAM_SHOT in message:
            print(">>> Handling topic shot camera: " + message)
            
            self.picture = self.camController.take_picture() 
            tupleblish = (PUB_TOPIC_ACK_PHOTO, self.picture)

            return tupleblish

        elif MSG_RESET in message:
            print(">>> Requested machine reset: " + message)
            
            time.sleep(3)
            machine.reset()

            return 

        elif MSG_SLEEP in message:
            self.working = False

        elif MSG_WORK in message:
            self.working = True

        elif MSG_VERSION in message:
            with open('/app/version.json') as jsonfile:
                version = json.load(jsonfile)['tag_version']
                tupleblish = (PUB_TOPIC_ACK_ESP, 'version:{}'.format(version))
                
                return tupleblish

    # ------------------------- SUB_TOPIC_ECHO -------------------------

    def echo_message(self, message):
        """
        Recibe una cadena de texto y la devuelve por <PUB_TOPIC_ACK_ESP>.

        Args:
            message (str): String para enviar por <PUB_TOPIC_ACK_ESP>

        Returns:
            (tuple): Tupla con el topico <PUB_TOPIC_ACK_ESP> y <message>
        """

        print(">>> Echo of: " + message)
        tupleblish = (PUB_TOPIC_ACK_ESP, message)

        return tupleblish
    
     # -------------------------- START POINT --------------------------
    
    def process_message(self, topic_bin, payload_bin):
        """
        Recibe un topico <topic_bin> y un payload <payload>, y dependiendo del topico,
        asigna la funcion que lo va a procesar, en base a lo definido en <self.topics_handlers>.

        Args:
            topic_bin (bin): Topico por el cual llego el mensaje
            payload_bin (bin): Mensaje

        Returns:
            (tuple): Tupla con el topico por donde se debe responder y la respuesta. (En el caso de que haya respuesta)
        """
    
        print(">>> Processing message...")
        topic_utf = topic_bin.decode('UTF-8')
        payload_utf = payload_bin.decode('UTF-8')

        if topic_utf in self.topics_handlers.keys():
            handler = self.topics_handlers[topic_utf]
            tupleblish =  handler(payload_utf)

            return tupleblish 
