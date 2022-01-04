from app.current.lib.MicroWebSrv2 import *
from app.current.lib.microDNSSrv import MicroDNSSrv
from time import sleep
import network 
import utime

ssid_ap = ""
password_ap = ""
credenciales_correctas = None

def search_wifi():   
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    redes_codificadas = sta_if.scan()
    redes_decodificadas = []

    for i in redes_codificadas:
        red_decodificada = i[0].decode('UTF-8')
        redes_decodificadas.append(red_decodificada)

    return redes_decodificadas

def iniciar_servidor():
    global ssid_ap
    global password_ap
    global credenciales_correctas

    ap_if = network.WLAN(network.AP_IF)            # instancia el objeto -sta_if- para realizar la conexión en modo STA 
    ap_if.active(True)   
    ap_if.config(essid="Trimaker Nebula Plus")
    print(ap_if.ifconfig())

    #----------------------------------------------------------------#

    MicroDNSSrv.Create({ '*' : '192.168.4.1' })
    
    #----------------------------------------------------------------#
    
    @WebRoute(GET, '/')
    def RequestHandler(microWebSrv2, request):
        content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0'>
            <link rel="stylesheet" href="styles.css">
            <title>Trimaker</title>
        </head>
        <body>
            <div class="container">
            <header class="header">
                <div class="header__logo">
                    <img src="logoflare.png" alt="logo Trimaker">
                </div>
                <div class="header__title">
                    Wi-Fi
                </div>
                <div class="header__subtitle">
                    {bloque_html_2}
                </div>
                <hr class="separator">  
            </header>
            
            <main class="main">
                <form class="main__form" action="/loading" method="POST">
                    <select class="main__form__input main__form__select" name="ssid" id="ssid">
                        <option disabled selected>Red Wi-Fi</option>
                        {bloque_html_1}
                    </select>
                    <input class="main__form__input main__form__password" name="password" id="password" type="password" placeholder="Contraseña">
                    <input class="main__form__input main__form__button" type="submit" value="Conectar">
                </form>
            </main>
            
            <footer class="footer">
                <p class="footer__title">UNIVERSO TRIMAKER</p>
                <p class="footer__subtitle">www.trimaker.com</p>
            </footer>
            </div>
        </body>
        </html>
        """
        
        redes_wifi = search_wifi()

        bloque_html_1 = ""
        bloque_html_2 = "¡Te damos la bienvenida!"
        
        for red in redes_wifi:
            bloque_html_1 += """<option value="{}"> {}</option>""".format(red, red)

        if credenciales_correctas == False:
            bloque_html_2 = "Las credenciales ingresadas son incorrectas"
        
        content = content.format(bloque_html_1=bloque_html_1, bloque_html_2=bloque_html_2)

        request.Response.ReturnOk(content)

    #----------------------------------------------------------------#

    @WebRoute(POST, '/loading')
    def RequestTestPost(microWebSrv2, request) :
        data = request.GetPostedURLEncodedForm()

        global ssid_ap
        global password_ap

        try :
            ssid_ap = data['ssid']
            password_ap  = data['password']
        except :
            request.Response.ReturnBadRequest()

        content   = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0'>
            <link rel="stylesheet" href="styles.css">
            <meta http-equiv="Refresh" content="10;url=/check">
            <title>Trimaker</title>
        </head>
        <body>
            <div class="container">
            <header class="header">
                <div class="header__logo">
                    <img src="logoflare.png" alt="logo Trimaker">
                </div>
                <div class="header__title">
                    Wi-Fi
                </div>
                <hr class="separator">  
            </header>
            
            <main class="main">
                <div class="main__text">Por favor espera mientras validamos tus credenciales.</div>
                <img src="spinner.gif" alt="spinner" class="main__spinner">
            </main>
            
            <footer class="footer">
                <p class="footer__title">UNIVERSO TRIMAKER</p>
                <p class="footer__subtitle">www.trimaker.com</p>
            </footer>
            </div>
        </body>
        </html>
        """
        request.Response.ReturnOk(content)

    @WebRoute(GET, '/check')               
    def RequestHandler(microWebSrv2, request):
        global credenciales_correctas

        if credenciales_correctas:
            content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0'>
                <link rel="stylesheet" href="styles.css">
                <title>Trimaker</title>
            </head>
            <body>
                <div class="container">
                <header class="header">
                    <div class="header__logo">
                        <img src="logoflare.png" alt="logo Trimaker">
                    </div>
                    <div class="header__title">
                        Wi-Fi
                    </div>
                    <hr class="separator">  
                </header>
                
                <main class="main">
                    <div class="main__text">Conexión exitosa</div>
                    <div class="main__title">¡YA PUEDES DESPEGAR!</div>
                </main>
                
                <footer class="footer">
                    <p class="footer__title">UNIVERSO TRIMAKER</p>
                    <p class="footer__subtitle">www.trimaker.com</p>
                </footer>
                </div>
            </body>
            </html>
            """
            request.Response.ReturnOk(content)
        else:
            request.Response.ReturnRedirect('/')

    #----------------------------------------------------------------#

    mws2 = MicroWebSrv2()
    mws2.NotFoundURL = '/'
    mws2.SetEmbeddedConfig()
    mws2.RootPath = '/app/current/lib/www/'

    mws2.StartManaged()

    while credenciales_correctas != True:
        while ssid_ap == "" and password_ap == "":
            sleep(1)

        start = utime.time()
        timed_out = False
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(ssid_ap, password_ap)

        while sta_if.status() == network.STAT_CONNECTING and not timed_out:   

            if utime.time() - start >= 10:      
                timed_out = True

            utime.sleep_ms(1000)

        if timed_out:
            sta_if.active(False)
            credenciales_correctas = False
            ssid_ap = ""
            password_ap = ""
        else:
            credenciales_correctas = True

    return ssid_ap, password_ap