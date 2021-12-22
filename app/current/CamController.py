import machine
import camera
import time
import ntptime

from app.current import mqtt
from app.current.config import Config 

class CamController:
    """
    This class is responsable for:

    - Read config saved in config.json and configure cam with that parameters.
    - Initialize the camera.
    - Take a photo.
    - Modify a parameter and save on config.json.
    """

    def __init__(self):
        """
        This is the constructor of CamController objects, is responsible for:

        - Load parameters saved on config.json.
        - Initialize the camera.
        
        Parameters:
        - None
        """
        try:
            print("\n>>> ------------------ CAMERA INIT -----------------")
            time.sleep_ms(3000) # Wait for read logs into REPL

            # ----------------------------------------------------------------------------------
            # LOAD CONFIG AREA:
            # ---------------------------------------------------------------------------------- 
            self.__config = Config()

            self.__app_config = Config().load_config('app_config')
            self.__cam_config = Config().load_config('cam_config')
            self.__pins_config = Config().load_config('pins')
            
            self.__flash = machine.Pin(self.__pins_config['flash'], machine.Pin.OUT)   
            
            # ----------------------------------------------------------------------------------
            # SELECT CAM HARDWARE:
            # ---------------------------------------------------------------------------------- 
            if self.__cam_config['camera'] == 'ESP32-CAM':
                camera.init(0, format=camera.JPEG)  

            elif self.__cam_config['camera'] == 'M5CAMERA':
                camera.init (0, d0=32, d1=35, d2=34, d3=5,
                            d4=39, d5=18, d6=36, d7=19,
                            href=26, vsync=25, reset=15,
                            sioc=23, siod=22, xclk=27, pclk=21)   

            # ----------------------------------------------------------------------------------
            # SETUP CAM CONFIG:
            # ---------------------------------------------------------------------------------- 
            self.__whitebalance = {"WB_NONE": camera.WB_NONE,
                                   "WB_SUNNY": camera.WB_SUNNY,
                                   "WB_CLOUDY": camera.WB_CLOUDY,
                                   "WB_OFFICE": camera.WB_OFFICE,
                                   "WB_HOME": camera.WB_HOME  
                                  }

            camera.flip            (self.__cam_config['flip']) 
            camera.mirror          (self.__cam_config['mirror']) 
            camera.saturation      (self.__cam_config['saturation'])
            camera.brightness      (self.__cam_config['brightness'])
            camera.contrast        (self.__cam_config['contrast'])
            camera.quality         (self.__cam_config['quality'])
            camera.whitebalance    (self.__whitebalance[self.__cam_config['whitebalance']])

            print(">>> Camera configuration successfully loaded...\n")
            time.sleep_ms(3000) # Wait for read logs into REPL
        
        except Exception as e:
            print(">>> ERROR ocurred into camera init: " + str(e))
            time.sleep_ms(3000) # Wait for read logs into REPL

            if str(e) != '-202':
                print(">>> Machine reset...")
                time.sleep_ms(5000)
                machine.reset()
                
            else:
                print(">>> Exception -202 do not block the camara...")

    # ----------------------------------------------------------------------------------
    # METHODS AREA:
    # ----------------------------------------------------------------------------------

    def take_picture(self):
        """
        Take photo and return it. 

        Parameters:
        - None
        
        Return:
        - PHOTO <str>: 
        """
        self.__flash.value(1)
        time.sleep_ms(500)  # Stabilizing led light
        self.__buf = camera.capture()
        self.__flash.value(0)
        
        return self.__buf 
    

    def __is_number(self,s):
        """
        Evaluate if <s> is a number

        Parameters:
        - S <any> = Number to evaluate
        
        Return:
        - RESULT <bool>
        """
        try:
            float(s)
            return True

        except ValueError:
            return False


    def apply_setting(self, message):
        """
        Change parameter of camera

        Parameters and values available:
        - FLIP:         {0, 1}
        - MIRROR:       {0, 1}
        - SATURATION:   [-2.2 , 2] (default: 0)
        - BRIGHTNESS:   [-2.2 , 2] (default: 0)
        - CONTRAST:     [-2.2 , 2] (default: 0)
        - QUALITY:      [10, 63]   (default: 0) lower = higher quality
        - WHITEBALANCE: {WB_NONE, WB_SUNNY, WB_CLOUDY, WB_OFFICE, WB_HOME} (default: WB_NONE)

        Parameters:
        - MESSAGE <str> "<parameter_to_change>=<value>" = Parameter and value associated to change
        
        Return:
        - None
        """
        # ----------------------------------------------------------------------------------
        # SPLIT MESSAGE: We expect messages like this ---> "cam_saturation=1" 
        # ----------------------------------------------------------------------------------
        self.__msg_command = message.split("=")[0]  # Save the cam parameter to change: cam_size, cam_flip, cam_whitebalance
        self.__msg_value   = message.split("=")[1]  # Save the value to be changed of the parameter

        # ----------------------------------------------------------------------------------
        # PROCCESING MSG_VALUE: 
        # ----------------------------------------------------------------------------------
        # Integer: If __msg_value is a number, convert to integer (And nearest if float was passed)
        if self.__is_number(self.__msg_value):
            self.__msg_value_int = int(round(float(self.__msg_value)))

        # String: If not, just keep the string value. Example: "WB_SUNNY"
        else:   
            self.__msg_value_str = self.__msg_value

        # ----------------------------------------------------------------------------------
        # FLIP: 0 or 1 
        # ----------------------------------------------------------------------------------
        if self.__msg_command == mqtt.MSG_CAM_FLIP:
            # Check if __msg_value_int is in the accepted range
            if (self.__msg_value_int == 0 or self.__msg_value_int == 1):
                camera.flip(self.__msg_value_int)
                self.__config.save_config("flip",self.__msg_value_int)
                print(">>> Camera setting successfully applied!")
                return
            else:
                print(">>> Camera flip parameter out of range. Nothing to do.")
                return 

        # ----------------------------------------------------------------------------------
        # MIRROR: 0 or 1 
        # ----------------------------------------------------------------------------------
        elif self.__msg_command == mqtt.MSG_CAM_MIRROR:
            if (self.__msg_value_int == 0 or self.__msg_value_int == 1):
                camera.mirror(self.__msg_value_int)
                self.__config.save_config("mirror",self.__msg_value_int)
                print(">>> Camera setting successfully applied!")
                return
            else:
                print(">>> Camera mirror parameter out of range. Nothing to do.")
                return

        # ----------------------------------------------------------------------------------
        # SATURATION: (-2.2 , 2) (default 0)
        # ----------------------------------------------------------------------------------
        elif self.__msg_command == mqtt.MSG_CAM_SATURATION:
            if (-2 >= self.__msg_value_int <= 2 ):
                camera.saturation(self.__msg_value_int)
                self.__config.save_config("saturation",self.__msg_value_int)
                print(">>> Camera setting successfully applied!")
                return
            else:
                print(">>> Cammera saturation parameter out of range. Nothing to do.")
                return

        # ----------------------------------------------------------------------------------
        # BRIGHTNESS: (-2.2 , 2) (default 0)
        # ----------------------------------------------------------------------------------
        elif self.__msg_command == mqtt.MSG_CAM_BRIGHTNESS:
            if (-2 >= self.__msg_value_int <= 2 ):
                camera.brightness(self.__msg_value_int)
                self.__config.save_config("brightness",self.__msg_value_int)
                print(">>> Camera setting successfully applied!")
                return
            else:
                print(">>> Cammera brightness parameter out of range. Nothing to do.")
                return
        
        # ----------------------------------------------------------------------------------
        # CONTRAST: (-2.2 , 2) (default 0)
        # ----------------------------------------------------------------------------------
        elif self.__msg_command == mqtt.MSG_CAM_CONTRAST:
            if (-2 >= self.__msg_value_int <= 2 ):
                camera.contrast(self.__msg_value_int)
                self.__config.save_config("contrast",self.__msg_value_int)
                print(">>> Camera setting successfully applied!")
                return
            else:
                print(">>> Cammera contrast parameter out of range. Nothing to do.")
                return

        # ----------------------------------------------------------------------------------
        # QUALITY: (10, 63) (default 0) lower number means higher quality
        # ----------------------------------------------------------------------------------
        elif self.__msg_command == mqtt.MSG_CAM_CONTRAST:
            if (10 >= self.__msg_value_int <= 63 ):
                camera.quality(self.__msg_value_int)
                self.__config.save_config("quality",self.__msg_value_int)
                print(">>> Camera setting successfully applied!")
                return
            else:
                print(">>> Cammera quality parameter out of range. Nothing to do.")
                return

        # ----------------------------------------------------------------------------------
        # WHITEBALANCE: WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME
        # ----------------------------------------------------------------------------------
        elif self.__msg_command == mqtt.MSG_CAM_WHITEBALANCE:
            if self.__msg_value_str in self.__whitebalance:   
                camera.whitebalance(self.__whitebalance[self.__msg_value_str])
                self.__config.save_config("whitebalance",self.__msg_value_str)
                print(">>> Camera setting successfully applied!")
                return
            else:
                print(">>> Camera whitebalance parameter does not exist. Nothing to do.")
                return

        # ----------------------------------------------------------------------------------
        # MESSAGE IS INCORRECT
        # ----------------------------------------------------------------------------------
        else:
            print(">>> Message for cam settings does not match to any existing configuration. Nothing to do.")