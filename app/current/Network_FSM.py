import network
import utime

from app.current.PrinterController import PrinterController
from app.current import AP_server
from network_credentials_manager import NetworkCredentialsManager
from network_controller import NetworkController

# ----------------------------------------------------------------------------------
# VARIABLES AREA:
# ----------------------------------------------------------------------------------

AP = "AP"
FLASH = "FLASH"

class NetworkFSM():
    def __init__(self):
        self.credentials = None
        self.end_state_flag = None
        self.source = None
        self.state = None
        self.first_connection = True

        self.network_credentials_manager = NetworkCredentialsManager()
        self.network_controller = NetworkController()
        self.printer_controller = PrinterController()

    def connect_with_flash_credentials(self):
        self.credentials = self.network_credentials_manager.get_credentials()
        self.source = FLASH
        return self.connect_wifi
        
    def connect_wifi(self):
        connected = self.network_controller.connect_wifi(self.credentials)
        # Si no logre conectar intento con access point. En caso de que sea la primera conexion, sino sigo intentando con las credenciales en la flash
        if not connected: return self.access_point if self.first_connection else self.connect_wifi
        # En caso de conectar vamos al estado final
        return self.end_state

    def access_point(self):
        self.credentials = AP_server.iniciar_servidor()
        self.source = AP
        self.network_credentials_manager._append_wifi_credentials_locally(self.credentials[0], self.credentials[1])
        return self.connect_wifi

    def end_state(self):
        self.printer_controller.print_on_screen("M117 Conectada a WIFI por {}".format(self.source))
        self.end_state_flag = True

    def connect(self):
        self.end_state_flag = False
        self.state = self.connect_with_flash_credentials()

        while not self.end_state_flag:
            self.state = self.state()

        self.first_connection = False