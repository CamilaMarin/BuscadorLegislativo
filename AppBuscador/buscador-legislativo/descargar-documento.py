#!C:/ProgramData/Anaconda3/python.exe

#Imports
import sys, requests, psycopg2, socket, httpagentparser, cgi, os, httplib2
import pandas as pd
import urllib
from urllib.parse import urlparse
from urllib.parse import parse_qs
import urllib.request
from sqlalchemy import create_engine
from requests import get

#Globales
app_url = 'http://ureus26:8888/buscador-legislativo/'
sesion_data = requests.Session()
sesion_id = -1
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
conn = psycopg2.connect(host='localhost', dbname='buscadorlegislativo', user='postgres', password='bofil8937')
engine = create_engine('postgresql://postgres:bofil8937@localhost/buscadorlegislativo')
form = cgi.FieldStorage()

def comprobar_sesion():
    try:
        sdata = sesion_data.cookies.get_dict()        
        if len(sdata) == 0 :
            sesion_id = iniciar_sesion()
        else :
            sesion_id = sdata.get('sesion_id')
        return sesion_id
    except Exception as e:
        return 'Error al comprobar sesion ('+str(e)+')'

def iniciar_sesion() :
    try:
        #BD
        sql_str = "insert into sesiones (fechahora, idsuscriptor, navegador, so, ip) values (NOW(), 0, 'CHROME', 'WINNT', '"+ip_address+"') RETURNING idsesion;"
        sesion_id = ejecutar_cmd_bd(sql_str, True)        
        #Setear cookies
        sesion_cookie = {
            'version' : 0,
            'name' : 'sesion_id',
            'value' : sesion_id
            }

        sesion_data.cookies.set(**sesion_cookie)

    except Exception as e:
        return 'Error al iniciar sesion ('+str(e)+')'
    return sesion_id

def detectBrowser():
    agent = http.request.environ.get('HTTP_USER_AGENT')
    browser = httpagentparser.detect(agent)
    if not browser:
        browser = agent.split('/')[0]
    else:
            browser = browser['browser']['name']
    return browser

def abrir_conexion():
    try:
        conn = psycopg2.connect(host='localhost', dbname='buscadorlegislativo', user='postgres', password='bofil8937')
    except Exception as e:
        print('Error al abrir bd('+str(e)+')')

def cerrar_conexion():
    conn.close()

def ejecutar_cmd_bd(cmd_sql, identity = False):
    try:
        #abrir_conexion()
        cursor = conn.cursor()
        cursor.execute(cmd_sql)
        conn.commit()
        resultado = cursor.fetchone()[0]
        cerrar_conexion()
        if identity == True :
            return resultado            
    except Exception as e:
        print('Error al ejecutar cmd bd ('+str(e)+')')
    return sesion_id

def downloadFile(URL=None):    
    h = httplib2.Http(".cache")
    resp, content = h.request(URL, "GET")
    return content

def download(url, file_name):
    with open(file_name, "wb") as file:
        response = get(url)
        file.write(response.content)

def descargar_documento(iddocumento, idley):
    try:
        df = pd.read_sql_query('select archivo from proyectosleydocumentos where iddocumento='+iddocumento, con=engine)            
        for index, row in df.iterrows():
            nombre_doc = row['archivo']       

        url = app_url + 'docs/' + idley + '/' + urllib.parse.quote(nombre_doc)

        #downloadFile(url) 
        download(url, nombre_doc)

    except Exception as e:
        return 'Error al descargar archivo ('+str(e)+')'

def iniciar_ajax():
    #print("Content-Type: text/plain; charset=iso-8859-1\n")
    #sesion_id = comprobar_sesion()       
    #print('sesion_id:' + str(sesion_id))

    try:
        # Resultado  
        iddocumento = form["id"].value
        idley = form["ley"].value
        resultado = descargar_documento(iddocumento, idley)
        print(resultado)

    except Exception as e:
        print('Error al procesar request ('+str(e)+')')          
    
iniciar_ajax()