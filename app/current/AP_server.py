from app.current.lib.MicroWebSrv2 import *
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
    
    @WebRoute(GET, '/')
    def RequestHandler(microWebSrv2, request):
        content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0'>
            <title>Trimaker</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <div class="container">
                <img class="logo" src="logo.png" alt="logo trimaker">

                <h1 class="title">Bienvenido</h1>
                <h2 class="subtitle">Wi-Fi</h2>

                <form class="form" action="/loading" method="post">
                    <select class="form__input" name="ssid" id="ssid">
                        <option disabled selected>Red Wifi</option>
                        {bloque_html_1}
                    </select>
                    <input class="form__input" type="password" name="password" placeholder="Clave WIFI">
                    <input class="form__input form__button" type="submit" value="Conectar">
                    {bloque_html_2}
                </form>

                <footer>
                    www.trimaker.com
                </footer>
            </div>
        </body>
        </html>
        """
        
        redes_wifi = search_wifi()

        bloque_html_1 = ""
        bloque_html_2 = ""
        
        for red in redes_wifi:
            bloque_html_1 += """<option value="{}"> {}</option>""".format(red, red)

        if credenciales_correctas == False:
            bloque_html_2 = """Las credenciales ingresadas son incorrectas"""
        
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
            <meta http-equiv="Refresh" content="10;url=/check">
            <title>Trimaker</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <div class="container">
                <img class="logo" src="logo.png" alt="logo trimaker">
                <h1 class="subtitle">Corroborando credenciales</h1>
                <h1 class="subtitle">Por favor espere</h1>
                <img class="loading" src="loading.gif" alt="loading">
                <footer>
                www.trimaker.com
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
                <title>Trimaker</title>
                <link rel="stylesheet" href="styles.css">
            </head>
            <body>
                <div class="container">
                    <img class="logo" src="logo.png" alt="logo trimaker">
                    <h1 class="subtitle">Conexion exitosa</h1>
                    <footer>
                    www.trimaker.com
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