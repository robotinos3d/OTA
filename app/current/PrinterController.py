#------------------------------------------------------------------
# PrinterController.py
#------------------------------------------------------------------

############################# IMPORT ##############################

import machine
import time

############################ SINGLETON ############################

def singleton(cls):
    instances = dict()

    def wrap(*args,**kwargs):
        if cls not in instances:
            instances[cls] = cls(*args,**kwargs)
        return instances[cls]
    
    return wrap

######################## PRINTERCONTROLLER ########################

@singleton
class PrinterController(object):
    """
    Esta clase permite inicializar, recibir y enviar mensajes a traves de la UART.
    """

    def __init__(self):
        print(">>> ------------------ UART INIT -----------------")
        
        self.payload = {
            'x' : None,
            'y' : None,
            'z' : None,
            'ext_temp' : None,
            'bed_temp' : None,
            'ext_target' : None,
            'bed_target' : None,
            'printing' : None,
            '%' : None}

        self.__BAUDRATE = 115200                    
        self.__UART_NUMBER = 1
        self.__BITS = 8
        self.__PARITY = None
        self.__STOP = 1
        self.__PIN_TX = 13
        self.__PIN_RX = 12
        self.__IS_BUSY = False
        self.__RXBUF = 1024
        self.__TXBUF = 1024
        self.__UART = machine.UART(
                                   self.__UART_NUMBER,
                                   self.__BAUDRATE,
                                   tx=self.__PIN_TX,
                                   rx=self.__PIN_RX,
                                   rxbuf=self.__RXBUF,
                                   txbuf=self.__TXBUF
                                   )
        
        try:
            self.__UART.init(
                             self.__BAUDRATE,                                          
                             self.__BITS,
                             self.__PARITY,                          
                             self.__STOP                               
                             )       
                                         
            print(">>> UART succesfully initialized")
        except:
            print(">>> Something went south with UART init call MacGyver")

    # ------------------------- READ/SEND UART -------------------------

    def send_command(self, command):
        """
        Envia <command> a traves de la UART. 

        Args:
            command (str): Cadena de texto para enviar a traves de la UART.
        """

        written_chars = None
        written_chars = self.__UART.write(command)
        print(">>> Written chars to UART = " + str(written_chars))

    def read_line(self):
        """
        Verifica si hay mensajes en la UART. Si los hay, lee una linea y la devuelve.
        Si no hay mensajes en al UART, devuelve un string vacio. 

        Returns:
            (str): Linea leida de la UART.
        """

        response = ''
        
        if self.__UART.any():
            response = self.__UART.readline()
            return response
        else:
            print("Uart non available")
            return response

    def read_uart(self):
        """
        Verifica si hay mensajes en la UART. Si los hay, lee una linea y la devuelve.
        Si no hay mensajes en al UART, devuelve un string vacio. 

        Returns:
            (str): Linea leida de la UART.
        """

        buf = ""
        uart_char_number = 0
        uart_char_number = self.__UART.any()        

        if uart_char_number != 0:
            buf = self.read_line()
            buf_str = buf.decode()
            return buf_str

    # ----------------------------- PROCESS ------------------------------

    def reset_payload(self):
        """
        Setea en 'None' a cada uno de los valores almacenados en payload.
        """

        for key in self.payload.keys():
            self.payload[key] = None

    def process_uart(self):
        """
        Lee la UART y dependiendo del contenido, realiza las siguientes tareas:

        - UART vacia: Devuelve un string vacio.

        - Mensaje de temperatura en la UART: Rescata los valores, almacena la temperatura actual del extrusor, la temperatura actual
        de la cama, la temperatura objetivo del extrusor y la temperatura objetivo de la cama en <payload['ext_temp']>, 
        <payload['bed_temp']>,  <payload['ext_target']> y <payload['bed_target'], respectivamente.

        - Mensaje de posicion en la UART: Rescata la posicion, almacena la posicion de X, Y y Z en <payload['x']>, <payload['y']> y
        <payload['z']>, respectivamente.

        - Mensaje del estado de la impresion por SD: Rescata el estado y lo almacena en <payload['printing']>.

        - Otro mensaje: Devuelve el mensaje

        Returns:
            (str): Mensaje de la UART, que no sea temperatura, posicion o estado de impresion por SD.
        """

        line = self.read_uart()

        if not line: return ''

        if line == 'ok\n':
            return ''

        if all(('T:' in line, 'B:' in line)): # 'T:195.23 /195.00 B:59.74 /60.00 @:39 B@:127'
            data = line.split('@')[0] # 'T:195.23 /195.00 B:59.74 /60.00' 
            data = data.replace('T', '') # ':195.23 /195.00 B:59.74 /60.00' 
            data = data.replace('B', '') # ':195.23 /195.00 :59.74 /60.00'
            
            extruder_str = data.split(':')[1] # '195.23 /195.00 '
            bed_str = data.split(':')[2] # '59.74 /60.0'
            
            extruder_str = extruder_str.replace(' ', '') # '195.23/195.00'
            bed_str = bed_str.replace(' ', '') # '59.74/60.0'

            extruder_list = extruder_str.split('/') # ['195,23', '195,00']
            bed_list = bed_str.split('/') # ['59,74', '60,0']

            self.payload['ext_temp'] = float(extruder_list[0]) # 195,23
            self.payload['bed_temp'] = float(bed_list[0]) # 59,74
            self.payload['ext_target'] = float(extruder_list[1]) # 195,00
            self.payload['bed_target'] = float(bed_list[1]) # 60,0

        elif all(('X:' in line, 'Y:' in line, 'Z:' in line)): # 'X:58.0000 Y:100.0000 Z:0.2600 E:0.0000 Count X:4640 Y:8000 Z:104'
            splits = line.split() #  ['X:58.0000', 'Y:100.0000', 'Z:0.2600', 'E:0.0000', 'Count X:4640', 'Y:8000', 'Z:104']
            
            for i in range(3): # X Y Z
                axis, value = splits[i].split(':') # ['X', '58.000']
                self.payload[axis.lower()] = float(value)
        
        elif 'SD printing' in line: # 'Not SD printing' / 'SD printing byte 68722/3710702'
            if 'Not SD printing' in line:
                self.payload['printing'] = False
                self.payload['%'] = None

            elif 'SD printing byte' in line: # 'SD printing byte 68722/3710702'
                parcial_per_total_bytes_str = line[17:] # '68722/3710702'
                parcial_bytes_str, total_bytes_str = parcial_per_total_bytes_str.split('/') # '68722' '3710702' 
                self.payload['printing'] = True
                self.payload['%'] = int(parcial_bytes_str) // int(parcial_bytes_str) * 100 # 68722 // 3710702 * 100

        else:
            return line

    def get_payload(self):
        """
        Devuelve el payload y luego lo reinicia. 

        Returns:
            (str): payload
        """
        
        payload_str = str(self.payload)
        self.reset_payload()

        return payload_str
        
    # ------------------------------ GCODES ------------------------------

    def get_temp(self):
        """
        Solicita el reporte de las temperaturas.
        """

        self.send_command("M105\n")

    def get_pos(self):
        """
        Solicita la posicion actual.
        """

        self.send_command("M114\n")

    def get_sd_status(self):
        """
        Solicita el estado de la SD.
        """

        self.send_command("M27\n")

    def get_stats(self):
        """
        Solicita las estadisticas de la impresora.
        """

        self.send_command("M78\n")

    def get_information(self):
        """
        Solicita informacion a la impresora.
        """

        self.send_command("M115\n")
    
    def get_sd_files(self):
        """
        Solicita una lista de los archivos gcode que se encuentren en la SD.
        """

        self.send_command("M20\n")

    def send_echo(self, message):
        """
        Envia un echo al Marlin.
        """

        self.send_command("M118 E1 {}\n".format(message))

    def print_on_screen(self, message):
        """
        Imprime <message> en pantalla.

        Args:
            message (str): Cadena de texto para imprimir en pantalla
        """

        self.send_command("M117 {}\n".format(message))