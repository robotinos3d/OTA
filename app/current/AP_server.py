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
    print(ap_if.ifconfig())
    
    #----------------------------------------------------------------#

    @WebRoute(GET, '/')                               
    def RequestHandler(microWebSrv2, request):
        request.Response.ReturnRedirect('/login')

    #----------------------------------------------------------------#

    @WebRoute(GET, '/login')
    def RequestHandler(microWebSrv2, request):
        content = """
            <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Trimaker</title>
        </head>

        <body>
            <div class="container">
                <img class="logo" src="logo.png" alt="logo trimaker">

                <header>
                    <h1 class="title">Bienvenido</h1>
                </header>

                <h2 class="subtitle">Wi-Fi</h2>

                <form action="/loading" method="post">
                    <select name="ssid" id="ssid">
                        <option disabled selected> Red Wifi</option>
        """
        
        redes_wifi = search_wifi()
        
        for red in redes_wifi:
            content += """<option value="{}"> {}</option>""".format(red, red)

        content +=  """
                    </select><br />

                    <input type="password" name="password" placeholder=" Clave WIFI"><br />
                    <input class="button" type="submit" value="Conectar">
                </form>
        """
        if credenciales_correctas == False:
            content += """Las credenciales ingresadas son incorrectas<br /> """
        
        content += """
                <footer>
                    <br />
                    www.trimaker.com
                </footer>
            </div>

        </body>

        <style>
            body{
                width: 100%;
                height: 100%;
                background-color: #f5f5f5;
            }
            .container{
                margin-top: 25vh;
                width: 100%;
                height: 100%;
                font-family: system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans","Liberation Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
                display: flex;
                justify-content: space-around;
                align-items: center;
                flex-direction: column;
            }
            .title{
                font-size: 30px;
                font-weight: 400;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            .subtitle{
                font-size: 20px;
                font-weight: 300;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            select{
                border-radius: 3px;
                border-style: solid;
                border-color: grey 4;
                border-width: 1px;
                width: 306px;
                height: 45px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            input{
                border-radius: 3px;
                border-style: solid;
                border-color: grey 4;
                border-width: 1px;
                width: 300px;
                height: 40px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            .button{
                background-color: #0D6EFD;
                border: 0px;
                color: white;
                width: 306px;
            }
            footer{
                color: gray;
            }
            .logo{
                width: 80px;
            }
        </style>
        </html>
        """
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
            return

        content   = """
            <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Refresh" content="13;url=http://192.168.4.1/check">
            <title>Trimaker</title>
        </head>

        <body>
            <div class="container">
                <img class="logo" src="logo.png" alt="logo trimaker">
                
                <br />
                <header>
                    <h1 class="subtitle">Corroborando credenciales</h1>
                </header>
                <img class="loading" src="loading.gif" alt="loading">

                <footer>
                <br />
                www.trimaker.com
                </footer>
            </div>

        </body>

        <style>
            body{
                width: 100%;
                height: 100%;
                background-color: #f5f5f5;
            }
            .container{
                margin-top: 25vh;
                width: 100%;
                height: 100%;
                font-family: system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans","Liberation Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
                display: flex;
                justify-content: space-around;
                align-items: center;
                flex-direction: column;
            }
            .title{
                font-size: 30px;
                font-weight: 400;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            .subtitle{
                font-size: 20px;
                font-weight: 300;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            select{
                border-radius: 3px;
                border-style: solid;
                border-color: grey 4;
                border-width: 1px;
                width: 306px;
                height: 45px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            input{
                border-radius: 3px;
                border-style: solid;
                border-color: grey 4;
                border-width: 1px;
                width: 300px;
                height: 40px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            .button{
                background-color: #0D6EFD;
                border: 0px;
                color: white;
                width: 306px;
            }
            footer{
                color: gray;
            }
            .logo{
                width: 80px;
            }
            .loading{
                width: 80px;
            }
        </style>
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
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Trimaker</title>
        </head>

        <body>
            <div class="container">
                <img class="logo" src="logo.png" alt="logo trimaker">
                
                <br />
                <header>
                    <h1 class="subtitle">Su impresora se encuentra conectada a Wi-Fi</h1>
                </header>

                <footer>
                <br />
                www.trimaker.com
                </footer>
            </div>

        </body>

        <style>
            body{
                width: 100%;
                height: 100%;
                background-color: #f5f5f5;
            }
            .container{
                margin-top: 25vh;
                width: 100%;
                height: 100%;
                font-family: system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans","Liberation Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
                display: flex;
                justify-content: space-around;
                align-items: center;
                flex-direction: column;
            }
            .title{
                font-size: 30px;
                font-weight: 400;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            .subtitle{
                font-size: 20px;
                font-weight: 300;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            select{
                border-radius: 3px;
                border-style: solid;
                border-color: grey 4;
                border-width: 1px;
                width: 306px;
                height: 45px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            input{
                border-radius: 3px;
                border-style: solid;
                border-color: grey 4;
                border-width: 1px;
                width: 300px;
                height: 40px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            .button{
                background-color: #0D6EFD;
                border: 0px;
                color: white;
                width: 306px;
            }
            footer{
                color: gray;
            }
            .logo{
                width: 80px;
            }
            .loading{
                width: 80px;
            }
        </style>
        </html>
            """
        else:
            content = """
            <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Refresh" content="1;url=http://192.168.4.1/login">
            <title>Trimaker</title>
        </head>
        </html>"""  
        request.Response.ReturnOk(content)

    #----------------------------------------------------------------#

    mws2 = MicroWebSrv2()
    mws2.NotFoundURL = '/'
    mws2.SetEmbeddedConfig()
    mws2.RootPath = '/app/lib/www/'

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