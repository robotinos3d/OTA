#------------------------------------------------------------------
# token.py
#------------------------------------------------------------------

############################# IMPORT #############################

from app.current.config import Config
from app.current.PrinterController import PrinterController
import uos

############################## TOKEN ##############################

class Token:
    def __init__(self):
        self.config = Config()
        self.n_digits = self.config.load_config('token_config')['n_digits']

    def generate_token(self):
        """
        Genera un token de <self.n_digits> digitos y lo devuelve.

        Returns:
            (int): Token de <self.n_digits> digitos.
        """
        
        self.token_bin = uos.urandom(50) # b"\xc9B\xfa=F+\x81%`%T\xde\xf7w9'Qr\x92\xbe"
        self.token_hex = str(self.token_bin) # 'b"\xc9B\xfa=F+\x81%`%T\xde\xf7w9'Qr\x92\xbe"'
        self.token_list = [n for n in self.token_hex if n.isdigit()] # ['9', '8', '8', '1', '7', '9', '9', '2']
        self.token_list = self.token_list[:self.n_digits] # ['9', '8', '8', '1', '7']
        self.token = int("".join(self.token_list)) # 98817

        return self.token