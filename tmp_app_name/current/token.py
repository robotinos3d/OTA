#------------------------------------------------------------------
# token.py
#------------------------------------------------------------------

############################# IMPORT #############################

from app.current.config import Config
from id_manager import get_random_number

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
        return get_random_number(self.n_digits)