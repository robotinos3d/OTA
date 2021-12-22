#------------------------------------------------------------------
# config.py
#------------------------------------------------------------------

############################# IMPORT #############################

import json

############################# CONFIG #############################

class Config:

    def __init__(self):
        
        self.CONFIG_FILE = '/app/current/config.json'

    # ------------------------- LOAD/SAVE CONFIG -------------------------
    
    def load_config(self, key = None):
        """
        Devuelve el valor de la clave ingresada, guardada en el archivo config.json

        Args:
            key (str): Clave de primer orden para buscar en el archivo config.json. Si <key> es omitido,
            toma el valor None.

        Returns:
            (dict): Diccionario con las claves y valores de segundo orden pertenecientes a la clave <key>.
            Si <key> vale None, devuelve un diccionario con las claves y valores de primer orden.
        """

        try:
            with open(self.CONFIG_FILE, 'r') as json_file:                                       
                config = json.load(json_file)
                
                if key is None:
                    #No se especifico key
                    result = config
                
                else:
                    if key in config.keys():
                        #Se especifico key y existe
                        result = config[key]
                        
                    else:
                        #Se especifico key y NO existe
                        result = None                                                                                              
        
        except Exception as e:
            print(">>> ERROR ocurred while trying to read config.json file: " + str(e))  

        return result


    def save_config(self, key, value):
        """
        Guarda <value> como el valor de la clave de segundo orden <key> en el archivo config.json.

        Args:
            key (str): Clave de segundo orden para cambiar
            value (any): Nuevo valor para almacenar
        """
    
        config = self.load_config()                                                      

        for i in config.keys():
            
            for j in config[i].keys():                                                       

                if j == key:
                    config[i][key] = value

        with open(self.CONFIG_FILE, 'w') as json_file:                                               
            json.dump(config, json_file)                                                             

        config = self.load_config()

        print(">>> New configuration saved...")