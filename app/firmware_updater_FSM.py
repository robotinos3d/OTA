#------------------------------------------------------------------
# firmware_updater_FSM.py
#------------------------------------------------------------------

############################# IMPORT ##############################

import machine
import uos 
import time
import boot_logger as boot_logger

######################## GLOBAL VARIABLES #########################

end_state_flag = None
firmware_name = None

######################## GLOBAL CONSTANTS #########################

ENCODED_FIRMWARE_PREFIX = "firmware"
ENCODED_FIRMWARE_EXTENSION = ".txt"
READY_FIRMWARE_EXTENSION = ".READY"
LABEL_NEW_FILE = "new-file"
SEPARATOR = "|"

VERSION_FIRMWARE_FILE_NAME = "version.txt"
VERSION_OTA_FILE_NAME = ".version"
NEW_FOLDER_NAME = "new"
CURRENT_FOLDER_NAME = "current"
OLD_FOLDER_NAME = "old"

JOB_PATH = "/app"
SD_MOUNT_PATH = "/sd"
VERSION_OTA_FILE_PATH = "{}/{}".format(JOB_PATH, VERSION_OTA_FILE_NAME)
VERSION_FIRMWARE_FILE_PATH = "{}/{}/{}".format(JOB_PATH, CURRENT_FOLDER_NAME, VERSION_FIRMWARE_FILE_NAME) 
NEW_FOLDER_PATH = "{}/{}".format(JOB_PATH, NEW_FOLDER_NAME)
CURRENT_FOLDER_PATH = "{}/{}".format(JOB_PATH, CURRENT_FOLDER_NAME)
OLD_FOLDER_PATH = "{}/{}".format(JOB_PATH, OLD_FOLDER_NAME)

############################## STATES ##############################

class Flash:
    """
    Esta clase provee dos metodos: successful y error.
    Cada uno de estos metodos generan una serie de flashes para indicarle al usuario si ocurrio algun error o 
    si todo ocurrio correctamente.
    """
    
    def __init__(self, enable=False):
        self.succesful_flash_time = 0.5 # segundos
        self.error_flash_time = 2 # segundos
        self.flash = machine.Pin(4, machine.Pin.OUT)
        self.enable = enable
    
    def successful(self):
        """
        Este metodo genera un parpadero en el flash que tiene una duracion de <self.succesful_flash_time> segundos.
        """
        if (self.enable):
            self.flash.on()
            time.sleep(self.succesful_flash_time)
            self.flash.off()

    def error(self):
        """
        Este metodo genera un parpadero en el flash que tiene una duracion de <self.error_flash_time> segundos.
        """
        if (self.enable):
            self.flash.on()
            time.sleep(self.error_flash_time)
            self.flash.off()

class SearchNewFirmwareOnSD:
    """
    Este estado monta la SD y busca un archivo que comience con <ENCODED_FIRMWARE_PREFIX> y termine con <ENCODED_FIRMWARE_EXTENSION>.

    - Si encuentra el archivo: Pasa al estado <RemoveOldNewFolder>
    - Si no encuentra el archivo: Pasa al estado <SendLog>
    - Si la SD no se encuentra puesta: Termina el procesamiento de la maquina de estado.
    """

    def __init__(self):
        self.flash = Flash()
        self.boot_logger = boot_logger.BootLogger("sd_update_log.txt")

    def get_firmware_name(self, files):
        """
        Este metodo busca en <files> un elemento que comience con <ENCODED_FIRMWARE_PREFIX> y finalice con <ENCODED_FIRMWARE_EXTENSION>.
        En caso de encontrarlo devuelve el nombre completo del elemento

        Args:
            files (list): Lista de los archivos entre los cuales se debe buscar el elemento

        Returns:
            (str) : Nombre completo del elemento coincidente dentro de la lista <files> 
        """

        for file in files:
            if file.startswith(ENCODED_FIRMWARE_PREFIX) and file.endswith(ENCODED_FIRMWARE_EXTENSION):
                return file

    def process(self):
        """
        Este metodo sera ejecutado por la maquina de estados.
        """

        global end_state_flag
        global firmware_name
        
        self.boot_logger.log_write("> STATE: SEARCH NEW FIRMWARE ON SD")

        try:
            self.files = None
            self.sd = machine.SDCard()
            self.boot_logger.log_write("> Mounting SD card on {}".format(SD_MOUNT_PATH))
            uos.mount(self.sd, SD_MOUNT_PATH)
            # uos.chdir(SD_MOUNT_PATH)
            self.boot_logger.log_write("> SD mounted successfully")
            self.files = uos.listdir(SD_MOUNT_PATH)
            self.boot_logger.log_write("> '{}' files: ".format(SD_MOUNT_PATH) + str(self.files))

            firmware_name = self.get_firmware_name(self.files)

            if firmware_name:
                self.boot_logger.log_write("> New firmware found on SD")
                self.boot_logger.log_write("> Firmware name: '{}'".format(firmware_name))
                result = RemoveOldNewFolder()
            else:
                self.boot_logger.log_write("> No new firmware found on SD")
                result = SendLog()

            self.flash.successful()
            return result 

        except:
            self.boot_logger.log_write("> No SD inserted")
            self.flash.error()
            end_state_flag = True


class RemoveOldNewFolder:
    """
    Este estado elimina en caso de existir la carpeta <NEW_FOLDER_NAME>, del directorio <PATH_JOB>.

    - Al finalizar: Pasa al estado <CreateNewFolder>
    """

    def __init__(self):
        self.flash = Flash()
        self.boot_logger = boot_logger.BootLogger("sd_update_log.txt")

    def rmdir(self, dir):
        """
        Este metodo elimina de manera recursiva el directorio y todos los archivos/subdirectorios que el mismo contenga.

        Args:
            dir (str): Path de la carpeta que se desea eliminar.
        """

        for element in uos.listdir(dir):
            if '.' in element: # es un archivo
                self.boot_logger.log_write("> Removing file '{}/{}'".format(dir, element))
                uos.remove('{}/{}'.format(dir, element))
            else: # es una carpeta
                self.rmdir('{}/{}'.format(dir, element))
        self.boot_logger.log_write("> Removing directory '{}'".format(dir))
        uos.rmdir(dir)

    def process(self):
        """
        Este metodo sera ejecutado por la maquina de estados.
        """

        self.boot_logger.log_write("> STATE: REMOVE OLD NEW FOLDER")
        self.files = uos.listdir(JOB_PATH)
        self.boot_logger.log_write("> '{}' files: ".format(JOB_PATH) + str(self.files))
        
        try:
            if NEW_FOLDER_NAME in self.files:
                self.boot_logger.log_write("> '{}' was found".format(NEW_FOLDER_NAME))
                self.boot_logger.log_write("> Removing files from '{}'".format(NEW_FOLDER_NAME))
                self.rmdir(NEW_FOLDER_PATH)
            else:
                self.boot_logger.log_write("> '{}' was not found".format(NEW_FOLDER_NAME))
        except Exception as e:
            self.boot_logger.log_write("> Problem to remove '{}'".format(NEW_FOLDER_NAME))
            
        self.flash.successful() 
        return CreateNewFolder()


class CreateNewFolder:
    """
    Este estado crea la carpeta <NEW_FOLDER_NAME> en el directorio <NEW_FOLDER_PATH>.

    - Al finalizar: Pasa al estado <UnzipFirmware>
    """

    def __init__(self):
        self.flash = Flash()
        self.boot_logger = boot_logger.BootLogger("sd_update_log.txt")

    def process(self):
        """
        Este metodo sera ejecutado por la maquina de estados.
        """

        self.boot_logger.log_write("> STATE: CREATE NEW FOLDER")
        uos.mkdir(NEW_FOLDER_PATH)
        self.boot_logger.log_write("> Make a '{}' folder".format(NEW_FOLDER_PATH))
        
        self.flash.successful()
        return UnzipFirmware()


class UnzipFirmware:
    """
    Este estado abre el firmware 'comprimido' ubicado en <NEW_FOLDER_PATH> y crea los distintos archivos con sus respectivos
    subdirectorios, logrando asi 'descomprimir' el fichero.

    - Al finalizar: Pasa al estado <MoveInstructionsToRoot>
    """

    def __init__(self):
        self.flash = Flash()
        self.boot_logger = boot_logger.BootLogger("sd_update_log.txt")
    
    def process_new_file_line(self, line_new_file):
        """
        Este metodo procesa las lineas que contienen una declaracion del tipo new_file.
        Crea los subdirectorios que alojan al archivo, y devuelve el path absoluto del archivo que debe ser creado.

        Args:
            line_new_file (str): Linea con la declaracion de 'new file' con la forma: <LABEL_NEW_FILE> <SEPARATOR> <relative_path_of_new_file>.

        Returns:
            (str): Path absoluto del archivo que debe ser creado.
        """

        relative_path_with_filename = line_new_file.split(SEPARATOR)[1]  # relative_path_with_filename = 'folder1\folder2\file.py'
        self.boot_logger.log_write("> relative_path_with_filename = {}".format(relative_path_with_filename))

        if '/' in relative_path_with_filename: # si la ruta relativa tiene subdirectorios entonces entra a este condicional y los crea.
            list_relative_path_with_filename = relative_path_with_filename.split("/") # list_relative_path_with_filename = ['folder1', 'folder2', 'file.py'] 
            self.boot_logger.log_write("> list_relative_path_with_filename = {}".format(list_relative_path_with_filename))
            
            list_relative_path_of_file = list_relative_path_with_filename[:-1] # relative_path_of_file = ['folder1', 'folder2']
            self.boot_logger.log_write("> list_relative_path_of_file = {}".format(list_relative_path_of_file))
            
            for i in range(len(list_relative_path_of_file)): 
                try:
                    self.boot_logger.log_write("> making folder --> {NEW_FOLDER_PATH}/{relative_path}".format(
                        NEW_FOLDER_PATH = NEW_FOLDER_PATH,
                        relative_path = '/'.join(list_relative_path_of_file[:i + 1])
                    ))

                    uos.mkdir("{NEW_FOLDER_PATH}/{relative_path}".format(
                        NEW_FOLDER_PATH = NEW_FOLDER_PATH,
                        relative_path = '/'.join(list_relative_path_of_file[:i + 1])
                    )) # i = 0 destination_path/folder1 | i = 1 destination_path/folder1/folder2 

                except:
                    self.boot_logger.log_write("> directory already exists")
            
        self.boot_logger.log_write("> absolut path of file output --> {NEW_FOLDER_PATH}/{relative_path_with_filename}".format(
            NEW_FOLDER_PATH = NEW_FOLDER_PATH,
            relative_path_with_filename = relative_path_with_filename
        ))
        
        return "{NEW_FOLDER_PATH}/{relative_path_with_filename}".format(
            NEW_FOLDER_PATH = NEW_FOLDER_PATH, 
            relative_path_with_filename = relative_path_with_filename
        ) # destination_path/folder1/folder2/file.py

    def process(self):
        """
        Este metodo sera ejecutado por la maquina de estados.
        """

        self.boot_logger.log_write("> STATE: UNZIP FIRMWARE")

        with open('{SD_MOUNT_PATH}/{firmware_name}'.format(
            SD_MOUNT_PATH = SD_MOUNT_PATH, 
            firmware_name = firmware_name)) as file:
            
            path_file_writing = None
            writing_file = None

            while True:
                if path_file_writing:
                    writing_file = open(path_file_writing, 'a')

                while True:
                    line = file.readline() # Leo una linea

                    if not line: break # Si es la ultima linea finalizo el ciclo while

                    if LABEL_NEW_FILE in line and SEPARATOR in line: # Si es una linea de new_file la proceso
                        path_file_writing = self.process_new_file_line(line.rstrip())
                        break
                    else: # Si es una linea normal, la escribo en el archivo abierto
                       writing_file.write(line) 

                if writing_file: writing_file.close() # Si hay un archivo abierto lo cierro

                if not line: break # Si es la ultima linea finalizo el ciclo while

        self.boot_logger.log_write("> Successful decoding")
        # uos.remove("{}/{}".format(NEW_FOLDER_PATH, firmware_name))
        # self.boot_logger.log_write("> Removing firmware zip")
        self.flash.successful()
        return InstallNewFirmware()

            
class InstallNewFirmware:
    def __init__(self) -> None:
        self.flash = Flash()
        self.boot_logger = boot_logger.BootLogger("sd_update_log.txt")

    def process(self):
        self.boot_logger.log_write("> STATE: INSTALL NEW FIRMWARE")

        self.boot_logger.log_write("> Renombrando {} a {}".format(CURRENT_FOLDER_PATH, OLD_FOLDER_PATH))
        uos.rename(CURRENT_FOLDER_PATH, OLD_FOLDER_PATH)

        self.boot_logger.log_write("> Renombrando {} a {}".format(NEW_FOLDER_PATH, CURRENT_FOLDER_PATH))
        uos.rename(NEW_FOLDER_PATH, CURRENT_FOLDER_PATH)

        return RemoveOldFirmware()


class RemoveOldFirmware:
    def __init__(self) -> None:
        self.flash = Flash()
        self.boot_logger = boot_logger.BootLogger("sd_update_log.txt")

    def rmdir(self, dir):
        """
        Este metodo elimina de manera recursiva el directorio y todos los archivos/subdirectorios que el mismo contenga.

        Args:
            dir (str): Path de la carpeta que se desea eliminar.
        """

        for element in uos.listdir(dir):
            if '.' in element: # es un archivo
                self.boot_logger.log_write("> Removing file '{}/{}'".format(dir, element))
                uos.remove('{}/{}'.format(dir, element))
            else: # es una carpeta
                self.rmdir('{}/{}'.format(dir, element))
        self.boot_logger.log_write("> Removing directory '{}'".format(dir))
        uos.rmdir(dir)

    def process(self):
        self.boot_logger.log_write("> STATE: Remove Old Firmware")
        self.rmdir(OLD_FOLDER_PATH)

        return SetFirmwareVersion()


class SetFirmwareVersion:
    """
    Este estado obtiene la version del firmware que ha sido actualizado del directorio
    {VERSION_FIRMWARE_FILE_PATH} y lo escribe en el archvio {VERSION_OTA_FILE_PATH}.

    Al finalizar: Pasa al estado <ChangeExtensionFirmwareOnSD>
    """

    def __init__(self):
        self.flash = Flash()
        self.boot_logger = boot_logger.BootLogger("sd_update_log.txt")

    def process(self):
        """
        Este metodo sera ejecutado por la maquina de estados.
        """

        self.boot_logger.log_write("> STATE: SET FIRMWARE VERSION")

        with open(VERSION_FIRMWARE_FILE_PATH, 'r') as version_firmware_file:
            with open(VERSION_OTA_FILE_PATH, 'w') as version_ota_file:
                version_ota_file.write(version_firmware_file.readline())

        self.flash.successful()
        return ChangeExtensionFirmwareOnSD()


class ChangeExtensionFirmwareOnSD:
    """
    Este estado cambia la extension del firmware ubicado en la SD, de <ENCODED_FIRMWARE_EXTENSION> a <READY_FIRMWARE_EXTENSION>

    Al finalizar: Pasa al estado <SendLog>
    """

    def __init__(self):
        self.flash = Flash()
        self.boot_logger = boot_logger.BootLogger("sd_update_log.txt")

    def process(self):
        """
        Este metodo sera ejecutado por la maquina de estados.
        """

        self.boot_logger.log_write("> STATE: CHANGE EXTENSION FIRMWARE ON SD")
        self.boot_logger.log_write("> Changing firmware extension")
        
        try:
            firmware_name_ready = str(firmware_name.split('.')[0]) + READY_FIRMWARE_EXTENSION 
            uos.rename('{}/{}'.format(SD_MOUNT_PATH, firmware_name), '{}/{}'.format(SD_MOUNT_PATH, firmware_name_ready))
        except:
            pass
        
        self.flash.successful()
        return SendLog()


class SendLog:
    """
    Este estado envia el log generado que se encuentra en el directorio <SRC_LOG> definido en <boot_logger.py>,
    al directorio <DST_LOG> defino en <boot_logger.py>. Luego desmonta la SD.

    Al finalizar: Termina la ejecucion de la maquina de estado.
    """
    
    def __init__(self):
        self.flash = Flash()
        self.boot_logger = boot_logger.BootLogger("sd_update_log.txt")

    def process(self):
        """
        Este metodo sera ejecutado por la maquina de estados.
        """
        
        global end_state_flag
        
        self.boot_logger.log_write("> STATE: SEND LOG")
        
        uos.chdir('/')
        self.boot_logger.log_write("> Sending log to SD")
        self.boot_logger.write_log_on_sd()
        uos.umount(SD_MOUNT_PATH)

        self.flash.successful()
        end_state_flag = True 


def start():
    global end_state_flag
    
    state = SearchNewFirmwareOnSD()
    end_state_flag = False

    while True:
        state = state.process()
        if end_state_flag == True:
            break