#!C:/ProgramData/Anaconda3/python.exe

#Imports
import sys, requests, psycopg2, socket, httpagentparser, cgi, os
import pandas as pd
import urllib
from urllib.parse import urlparse
from urllib.parse import parse_qs
from sqlalchemy import create_engine
from http import cookies

#Globales
app_url = 'http://localhost/buscador-legislativo/'

sesion_id = -1
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
conn = psycopg2.connect(host='localhost', dbname='BuscadorLegislativo', user='postgres')
engine = create_engine('postgresql://postgres@localhost/BuscadorLegislativo')
form = cgi.FieldStorage()

def comprobar_sesion():
    try:
        sesion_data = requests.Session()
        response = sesion_data.get(app_url)        
        dict = response.cookies.get_dict()       
        if len(dict) == 0 :
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
        #sesion_data = requests.Session()
        #sesion_cookie = { 'version' : 0, 'name' : 'sesion_id', 'value' : sesion_id, 'port': 8888, 'domain':'ureus26', 'path':'/buscador-legislativo/',  'secure':False,
        #                 'expires':None, 'discard':True, 'comment':None, 'comment_url':None, 'rest':{}, 'rfc2109':False}
        #sesion_data.cookies.set(**sesion_cookie)
        
        #cookies = dict(sesion_id=sesion_cookie)
        #r = requests.get(app_url, cookies=sesion_cookie)
       
        myobj = {'sesion_id': sesion_id }
        x = requests.post(app_url, data = myobj, cookies = {"favcolor": "Red"})
        
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

def ejecutar_busqueda(cmd_busqueda, parametros):
    resultado = ''

    try :
        if cmd_busqueda == 'BUSCARINDEX' :
            dictParams = crear_diccionario(parametros);
            criterio = dictParams['criterio']
            usrquery = dictParams['usrquery']
            
            strWherePry = ''
            strWhereLeg = ''
            strWhereDoc = ''
            strWhereCom = ''

            total_resultados = 0
            m = ''

            if criterio == 'E' :
                strWherePry = 'where (upper(proyectosley.nombre)=\'' + usrquery.upper() + '\') '
                strWhereLeg = "where (concat(upper(diputados.nombre),upper(diputados.apellidopaterno)) LIKE '%%%%" + usrquery.upper() + "%%%%') "
                strWhereDoc = 'where (upper(proyectosleydocumentos.titulo)=\'' + usrquery.upper() + '\') '
                strWhereCom = 'where (upper(comisiones.nombre) = \'' + usrquery.upper() + '\') '
            else :
                matquery = usrquery.split(' ')
                if criterio == 'A' :
                    matquery = quitar_stopwords(matquery)                
                for m in matquery :
                    #Proyectos                    
                    strWherePry += (" (upper(proyectosley.nombre) like '%%%%" + m.upper() + "%%%%') or (upper(materias.nombre) like '%%%%" + m.upper() + "%%%%') or "+
                             "  (upper(proyectosley.numeroboletin) like '%%%%" + m.upper() + "%%%%') or ")                                        
                    #Documentos
                    strWhereDoc += (" (upper(proyectosleydocumentos.titulo) like '%%%%" + m.upper() + "%%%%') or (upper(proyectosleydocumentos.tipo) like '%%%%" + m.upper() + "%%%%') or "+
                             "(upper(proyectosley.nombre) like '%%%%" + m.upper() + "%%%%') or  (upper(proyectosley.numeroboletin) like '%%%%" + m.upper() + "%%%%') OR ")                               
                    #Comisiones
                    strWhereCom += " ((upper(comisiones.nombre) like '%%%%" + m.upper() + "%%%%')) or "
                    #Legisladores                    
                    strWhereLeg += " ((upper(diputados.nombre) LIKE '%%%%" + m.upper() + "%%%%') OR (upper(diputados.apellidopaterno) LIKE '%%%%" + m.upper() + "%%%%')) or " 

                if strWherePry != '':
                    strWherePry = 'where ' + strWherePry[0:len(strWherePry)-4]           
                if strWhereDoc != '':
                    strWhereDoc = 'where ' + strWhereDoc[0:len(strWhereDoc)-4]
                if strWhereCom != '':
                    strWhereCom = 'where ' + strWhereCom[0:len(strWhereCom)-4]
                if strWhereLeg != '':
                    strWhereLeg = 'where ' + strWhereLeg[0:len(strWhereLeg)-4]

            cmd_sqlPry = ("select '1P' as tiporeg, proyectosley.idproyectoley as c1,proyectosley.numeroboletin as c2,proyectosley.nombre as c3,"+
                "TO_CHAR(fechaingreso :: DATE, 'dd/mm/yyyy') as c4, lower(materias.nombre) c5, 0 as c6, count(resultados.idbusqueda) as c7 from proyectosley " +
                " inner join proyectosleymaterias on proyectosley.idproyectoley=proyectosleymaterias.idproyectoley " +
                " inner join materias on proyectosleymaterias.idmateria=materias.idmateria " +
                " left join resultados on proyectosley.idproyectoley=resultados.id and resultados.tipo='P' and resultados.picked='1' " +
                strWherePry +
                " group by proyectosley.idproyectoley,proyectosley.numeroboletin,proyectosley.nombre,proyectosley.fechaingreso, materias.nombre")

            cmd_sqlDoc = ("select '2D' as tiporeg, proyectosleydocumentos.iddocumento as c1, proyectosleydocumentos.tipo as c2, proyectosleydocumentos.titulo as c3, " +
                " TO_CHAR(proyectosleydocumentos.fecha :: DATE, 'dd/mm/yyyy') as c4, proyectosley.nombre as c5, proyectosley.idproyectoley as c6, count(resultados.idbusqueda) as c7 "+
                " from proyectosleydocumentos " +
                " left join proyectosley on proyectosleydocumentos.idproyectoley=proyectosley.idproyectoley " +
                " left join resultados on iddocumento=resultados.id and resultados.tipo='D' and resultados.picked='1' " +
                strWhereDoc +
                " group by proyectosleydocumentos.iddocumento, proyectosleydocumentos.tipo, proyectosleydocumentos.titulo, " +
                " proyectosleydocumentos.fecha, proyectosley.nombre, proyectosley.idproyectoley") 

            cmd_sqlCom = ("select '3C' as tiporeg, comisiones.idcomision as c1, comisiones.nombre as c2, TO_CHAR(fechainicio :: DATE, 'dd/mm/yyyy') as c3, '' as c4, '' as c5, 0 as c6, count(idbusqueda) as c7 " +
                " from comisiones left join resultados on comisiones.idcomision=resultados.id and resultados.tipo='C' and resultados.picked='1' " + 
                strWhereCom +
                " group by comisiones.idcomision, comisiones.nombre")
            
            cmd_sqlLeg = ("select '4L' as tiporeg, diputados.iddiputado as c1, CONCAT(nombre,' ',apellidopaterno) as c2, '' as c3, partidoalias c4, "+
                "CONCAT(upper(nombre),'-',upper(apellidopaterno)) as c5, distrito as c6, 0 as c7 "+
                " from diputados inner join diputadosperiodo on diputados.iddiputado=diputadosperiodo.iddiputado " + strWhereLeg)

            cmd_sql = '('+ cmd_sqlPry + ') union (' + cmd_sqlDoc + ') union (' + cmd_sqlCom + ') union (' + cmd_sqlLeg + ') order by c7 desc, tiporeg asc'
            #return cmd_sql
            df = pd.read_sql_query(cmd_sql, con=engine)
            total_resultados = df.shape[0]
            for index, row in df.iterrows():
                if row['tiporeg'] == '1P':
                    resultado += ("<div class='dvtbResultado'>"+
                        "<table class='tbResultado'>"+
                        "<tr><td colspan='2' class='tbResultadoEpigrafe'><b>Proyecto de Ley</b> &bull; Boletín: {}</td></tr>"+
                        "<tr><th colspan='2'><a href=\"javascript:VerProyecto('{}', {})\">{}</a></th></tr>"+
                        "<tr><td colspan='2' style='text-align:justify'>Materias: {}</td></tr>"+
                        "<tr><td class='tbResultadoFecha'>Fecha ingreso: {} &bull; Número de visitas: <b>{}</b></td>"+
                        "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Visitar' onclick=\"javascript:VerProyecto('{}', {})\" /></td></tr>"+
                        "</table></div>").format(row['c2'], row['c3'], row['c1'], row['c3'], row['c5'], row['c4'], row['c7'], row['c3'], row['c1'])
                if row['tiporeg'] == '2D':
                    resultado += ("<div class='dvtbResultado'>"+
                        "<table class='tbResultado'>"+
                        "<tr><td colspan='2' class='tbResultadoEpigrafe'><b>Documento</b> &bull; Tipo: {}</td></tr>"+
                        "<tr><th colspan='2'><a href=\"javascript:DescargarDocumento({}, {})\">{}</a></th></tr>"+
                        "<tr><td colspan='2' style='text-align:justify'>Materias: {}</td></tr>"+
                        "<tr><td class='tbResultadoFecha'>Fecha publicación: {} &bull; Número de descargas: <b>{}</b></td>"+
                        "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Visitar' onclick=\"javascript:DescargarDocumento({}, {})\" /></td></tr>"+
                        "</table></div>").format(row['c2'], row['c1'], row['c6'], row['c3'], row['c5'], row['c4'], row['c7'], row['c3'], row['c1'])
                if row['tiporeg'] == '3C':
                    resultado += ("<div class='dvtbResultado'>"+
                        "<table class='tbResultado'>"+
                        "<tr><td colspan='2' class='tbResultadoEpigrafe'><b>Comisión</b> &bull; Tipo: Permanente</td></tr>"+
                        "<tr><th colspan='2'><a href=\"javascript:VerComision('{}','{}')\">{}</a></th></tr>" +
                        "<tr><td class='tbResultadoFecha'>Fecha inicio: {} &bull; Número de visítas <b>{}</b></td>" +
                        "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Ver comisión' onclick=\"VerComision('{}','{}')\" /></td></tr>" +
                        "</table></div>").format(row['c2'].replace(' ', '-').upper(), row['c1'], row['c2'], row['c3'], str(row['c7']),row['c2'].replace(' ', '-').upper(), row['c1'])
                if row['tiporeg'] == '4L':
                    resultado += ("<div class='dvtbResultado'>"+
                        "<table class='tbResultado'>"+
                        "<tr><td rowspan='4'><img src='imgs/legisladores/img-{}.jpg' alt='{}' style='width:100%; max-width:150px'></td></tr>"+
                        "<tr><td colspan='2' class='tbResultadoEpigrafe'><b>Legislador</b> &bull; Distrito: {}</td></tr>"+
                        "<tr><th colspan='2'><a href=\"javascript:VerLegislador('{}','{}')\">{}</a></th></tr>" +
                        "<tr><td class='tbResultadoFecha'>Partido: {}</td>" +
                        "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Ver comisión' onclick=\"VerLegislador('{}','{}')\" /></td></tr>" +
                        "</table></div>").format(row['c1'], row['c2'], str(row['c6']), row['c2'].replace(' ', '-').upper(), row['c1'], row['c2'], row['c4'], row['c2'].replace(' ', '-').upper(), row['c1'])

            return resultado + '|' + usrquery.upper() + '|' + str(df.shape[0])

        if cmd_busqueda == 'LISTARLEGISLADORES' :
            cmd_sql = ("select diputados.iddiputado, CONCAT(nombre,' ',apellidopaterno) as nombre_diputado, distrito, partidoalias, "+
                "CONCAT(upper(nombre),'-',upper(apellidopaterno)) as nombre_url "
                " from diputados inner join diputadosperiodo on diputados.iddiputado=diputadosperiodo.iddiputado "+
                " where (extract(year from fechainicio)=2018) order by nombre_diputado")
            df = pd.read_sql_query(cmd_sql, con=engine)
            #resultado = str(df.shape)
            for index, row in df.iterrows():
                  resultado += ("<div class='card'>"+
                        "<img src='imgs/legisladores/img-{}.jpg' alt='{}' style='width:100%; max-width:150px'>"+
                        "<h1>{}</h1>"+
                        "<p class='card-title'>Distrito {}</p>"+
                        "<p class='card-title'>{}</p>"+
                        "<p><button onclick=\"VerLegislador('{}','{}')\">Ver antecedentes</button></p>"+
                        "</div>").format(str(row['iddiputado']), row['nombre_diputado'], row['nombre_diputado'], str(row['distrito']), row['partidoalias'], row['nombre_url'], str(row['iddiputado']))

        if cmd_busqueda == 'BUSCARLEGISLADORES' :
             dictParams = crear_diccionario(parametros);
             usrquery = dictParams['usrquery']             
             matquery = usrquery.split(' ')             
             strWhere = ''
             for m in matquery :
                 strWhere += " AND ((upper(nombre) LIKE '%%%%" + m.upper() + "%%%%') OR (upper(apellidopaterno) LIKE '%%%%" + m.upper() + "%%%%'))"
                 
             cmd_sql = ("select diputados.iddiputado, CONCAT(nombre,' ',apellidopaterno) as nombre_diputado, distrito, partidoalias, "+
                "CONCAT(upper(nombre),'-',upper(apellidopaterno)) as nombre_url "
                " from diputados inner join diputadosperiodo on diputados.iddiputado=diputadosperiodo.iddiputado "+
                " where (extract(year from fechainicio)=2018) " + strWhere + " order by nombre_diputado")            
             #return cmd_sql
             df = pd.read_sql_query(cmd_sql, con=engine)
             for index, row in df.iterrows():
                  resultado += ("<div class='card'>"+
                        "<img src='imgs/legisladores/img-{}.jpg' alt='{}' style='width:100%; max-width:150px'>"+
                        "<h1>{}</h1>"+
                        "<p class='card-title'>Distrito {}</p>"+
                        "<p class='card-title'>{}</p>"+
                        "<p><button onclick=\"VerLegislador('{}','{}')\">Ver antecedentes</button></p>"+
                        "</div>").format(str(row['iddiputado']), row['nombre_diputado'], row['nombre_diputado'], str(row['distrito']), row['partidoalias'], row['nombre_url'], str(row['iddiputado']))

        if cmd_busqueda == 'BUSCARLEGISLADOR' :
             dictParams = crear_diccionario(parametros);
             iddiputado = dictParams['iddiputado']
             cmd_sql = ("select concat(diputados.iddiputado,'|'," +
                    "diputados.nombre,'|',diputados.apellidopaterno,'|',diputados.telefono,'|',diputados.email,'|',diputados.twitter,'|',partidoalias,'|',diputadosperiodo.distrito,'|',regiones.nombre) " +
                    " as datosdiputado, comunas.nombre as nombrecomuna from diputados inner join diputadosperiodo on diputados.iddiputado=diputadosperiodo.iddiputado " +
                    " inner join comunas on diputadosperiodo.distrito=comunas.distrito " +
                    " inner join provincias on comunas.idprovincia = provincias.idprovincia " +
                    " inner join regiones on provincias.idregion = regiones.idregion " +
                    " where diputados.iddiputado="+iddiputado)
             df = pd.read_sql_query(cmd_sql, con=engine)
             comunas = ''
             for index, row in df.iterrows():
                 resultado = row['datosdiputado']
                 comunas += row['nombrecomuna'] + ', '
             resultado += '|' + comunas

             cmd_sql = ("select comisiones.idcomision, comisiones.nombre from comisiones inner join integrantescomision on comisiones.idcomision=integrantescomision.idcomision where iddiputado="+iddiputado)
             df = pd.read_sql_query(cmd_sql, con=engine)
             comisiones = ''
             for index, row in df.iterrows():
                 comisiones += '<li><a href=\'comision.htm?comision=' + row['nombre'].replace(' ', '-').upper() + '&id='+ str(row['idcomision']) + '\'>' + row['nombre'] + '</a></li>'             
             resultado += '|' + comisiones

        if cmd_busqueda == 'LISTARCOMISIONES' :
            cmd_sql = ("select comisiones.idcomision, comisiones.nombre, count(idbusqueda) as total_busquedas, TO_CHAR(fechainicio :: DATE, 'dd/mm/yyyy') as fechainicio  " +
                " from comisiones left join busquedas on busquedas.ambito='COMISIONES' WHERE (extract(year from fechainicio)>=2018) " +
                " group by comisiones.idcomision, comisiones.nombre order by comisiones.nombre")
            df = pd.read_sql_query(cmd_sql, con=engine)
            total_resultados = str(df.shape[0])
            for index, row in df.iterrows():
                  resultado += ("<div class='dvtbResultado'>"+
                        "<table class='tbResultado'>" +
                        "<tr><td colspan='2' class='tbResultadoEpigrafe'>Tipo: <span style='color:#222'>Comisión permanente</span></td></tr>" +
                        "<tr><th colspan='2'><a href=\"javascript:VerComision('{}','{}')\">{}</a></th></tr>" +
                        "<tr><td class='tbResultadoFecha'>Fecha inicio: {} &bull; Número de visítas <b>{}</b></td>" +
                        "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Ver comisión' onclick=\"VerComision('{}','{}')\" /></td></tr>" +
                        "</table>" +
                        "</div>").format(row['nombre'].replace(' ', '-').upper(), row['idcomision'], row['nombre'], str(row['fechainicio']), str(row['total_busquedas']),  row['nombre'].replace(' ', '-').upper(), row['idcomision'])
            resultado += '|' + total_resultados

        if cmd_busqueda == 'BUSCARCOMISIONES' :
             total_resultados = 0
             dictParams = crear_diccionario(parametros);
             criterio = dictParams['criterio']
             usrquery = dictParams['usrquery']             
             matquery = usrquery.split(' ')
             strWhere = ''
             if criterio == 'A' :
                matquery = quitar_stopwords(matquery)
                                                    
             if criterio == 'T' or criterio == 'A' :
                 for m in matquery :
                     strWhere += " ((upper(comisiones.nombre) like '%%%%" + m.upper() + "%%%%')) or "
                 strWhere = 'where ' + strWhere[0:len(strWhere)-3]

             if criterio == 'E' :
                strWhere = 'WHERE (upper(comisiones.nombre) = \'' + usrquery.upper() + '\') '
                 
             cmd_sql = ("select comisiones.idcomision, comisiones.nombre, count(idbusqueda) as total_busquedas, TO_CHAR(fechainicio :: DATE, 'dd/mm/yyyy') as fechainicio " +
                " from comisiones left join resultados on comisiones.idcomision=resultados.id and resultados.tipo='C' and resultados.picked='1' " + strWhere +
                " group by comisiones.idcomision, comisiones.nombre order by comisiones.nombre")
             #return cmd_sql
             df = pd.read_sql_query(cmd_sql, con=engine)
             total_resultados = str(df.shape)
             total_resultados = df.shape[0]
             for index, row in df.iterrows():
                  resultado += ("<div class='dvtbResultado'>"+
                        "<table class='tbResultado'>" +
                        "<tr><td colspan='2' class='tbResultadoEpigrafe'>Tipo: <span style='color:#222'>Comisión permanente</span></td></tr>" +
                        "<tr><th colspan='2'><a href=\"javascript:VerComision('{}','{}')\">{}</a></th></tr>" +
                        "<tr><td class='tbResultadoFecha'>Última actualización: 20/08/2020 &bull; Número de visítas <b>{}</b></td>" +
                        "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Descargar' onclick=\"VerComision('{}','{}')\" /></td></tr>" +
                        "</table>" +
                        "</div>").format(row['nombre'].replace(' ', '-').upper(), str(row['idcomision']), row['nombre'], str(row['fechainicio']),
                                        str(row['total_busquedas']), row['nombre'].replace(' ', '-').upper(), str(row['idcomision']))            
             resultado += '|' + str(total_resultados)
             
        if cmd_busqueda == 'BUSCARCOMISION' :
             dictParams = crear_diccionario(parametros);
             idcomision = dictParams['idcomision']
             cmd_sql = ("select comisiones.nombre, comisiones.telefono, comisiones.correo, " +
                   " diputados.iddiputado, CONCAT(diputados.nombre,' ',diputados.apellidopaterno) as nombre_diputado, diputadosperiodo.distrito, " +
                   " diputadosperiodo.partidoalias, " +
                   " CONCAT(upper(diputados.nombre),'-',upper(diputados.apellidopaterno)) as nombre_url " +
                   " from comisiones " +
                   " left join integrantescomision on comisiones.idcomision=integrantescomision.idcomision " +
                   " left join diputados on integrantescomision.iddiputado=diputados.iddiputado " +
                   " left join diputadosperiodo on diputados.iddiputado=diputadosperiodo.iddiputado " +
                   " where comisiones.idcomision="+idcomision)           
             df = pd.read_sql_query(cmd_sql, con=engine)
             integrantes = ''
             for index, row in df.iterrows():
                 resultado = row['nombre'] + '|' + row['telefono'] + '|' + row['correo']
                 if row['nombre_diputado'] != ' ' :
                     integrantes += ("<div class='card'>"+
                        "<img src='imgs/legisladores/img-{}.jpg' alt='{}' style='width:100%; max-width:150px'>"+
                        "<h1>{}</h1>"+
                        "<p class='card-title'>Distrito {}</p>"+
                        "<p class='card-title'>{}</p>"+
                        "<p><button onclick=\"VerLegislador('{}','{}')\">Ver antecedentes</button></p>"+
                        "</div>").format(str(row['iddiputado']), row['nombre_diputado'], row['nombre_diputado'], str(row['distrito']), row['partidoalias'], row['nombre_url'], str(row['iddiputado']))
                 else :
                     integrantes = '<div id=\"dvSinAtencedentes\">Sin antecedentes</div>'                 
             resultado += '|' + integrantes
             cmd_sql = ("select idproyectoley, nombre from proyectosley limit 3")
             df = pd.read_sql_query(cmd_sql, con=engine)
             proyectos = ''
             for index, row in df.iterrows():
                 proyectos += '<li><a href=\'proyecto.htm?proyecto=' + row['nombre'].replace(' ', '-').upper() + '&id='+ str(row['idproyectoley']) + '\'>' + row['nombre'] + '</a></li>'             
             resultado += '|' + proyectos

        if cmd_busqueda == 'LISTARDOCUMENTOS' :
            cmd_sql = ("select proyectosleydocumentos.iddocumento, proyectosleydocumentos.tipo, proyectosleydocumentos.titulo, proyectosley.idproyectoley, " +
                " proyectosleydocumentos.fecha, proyectosley.nombre as nombreley, proyectosley.numeroboletin, count(resultados.idbusqueda) total_descargas,TO_CHAR(proyectosleydocumentos.fecha :: DATE, 'dd/mm/yyyy') as fechapub "+
                " from proyectosleydocumentos " +
                " left join proyectosley on proyectosleydocumentos.idproyectoley=proyectosley.idproyectoley " +
                " left join resultados on iddocumento=resultados.id and resultados.tipo='D' and resultados.picked='1' " +
                " WHERE (extract(year from fecha)<=2020) " +
                " group by proyectosleydocumentos.iddocumento, proyectosleydocumentos.tipo, proyectosleydocumentos.titulo, proyectosley.numeroboletin, " +
                " proyectosleydocumentos.fecha, proyectosley.nombre, proyectosley.idproyectoley order by fecha desc limit 20") 
            
            df = pd.read_sql_query(cmd_sql, con=engine)            
            for index, row in df.iterrows():
                  resultado += ("<div class='dvtbResultado'><table class='tbResultado'>"+                    
                    "<tr><td colspan='3' class='tbResultadoEpigrafe'>Tipo: {} • Boletín: {}</td></tr>"+
                    "<tr><th colspan='3'><a href='javascript:DescargarDocumento({}, {})'>{}</a></th></tr>     "+
                    "<tr><td colspan='3'>Referencia: {}</td></tr>"+
                    "<tr><td class='tbResultadoFecha'>Fecha publicación: {} &bull; Número de descargas <b>{}</b></td>"+                    
                    "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/prv.svg' alt='Previsualizar' onclick='javascript:VisualizarDocumento()' /></td>"+
                    "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/dwn.svg' alt='Descargar' onclick='javascript:DescargarDocumento({}, {})' /></td>"+
                    "</tr></table></div>").format(row['tipo'], row['numeroboletin'], str(row['iddocumento']), str(row['idproyectoley']), row['titulo'], row['nombreley'], row['fechapub'], str(row['total_descargas']),str(row['iddocumento']),  str(row['idproyectoley']))

        if cmd_busqueda == 'BUSCARDOCUMENTOS' :
            dictParams = crear_diccionario(parametros);
            criterio = dictParams['criterio']
            usrquery = dictParams['usrquery']
            
            strWhere = ''
            total_resultados = 0
                       
            if criterio == 'E' :
                strWhere = 'where (upper(proyectosleydocumentos.titulo)=\'' + usrquery.upper() + '\') '
            else :
                matquery = usrquery.split(' ')
                if criterio == 'A' :
                    matquery = quitar_stopwords(matquery)
                for m in matquery :
                    strWhere += (" (upper(proyectosleydocumentos.titulo) like '%%%%" + m.upper() + "%%%%') or (upper(proyectosleydocumentos.tipo) like '%%%%" + m.upper() + "%%%%') or "+
                             "(upper(proyectosley.nombre) like '%%%%" + m.upper() + "%%%%') or  (upper(proyectosley.numeroboletin) like '%%%%" + m.upper() + "%%%%') OR ")            
                if strWhere != '':
                    strWhere = 'where ' + strWhere[0:len(strWhere)-4]
            
            cmd_sql = ("select proyectosleydocumentos.iddocumento, proyectosleydocumentos.tipo, proyectosleydocumentos.titulo, proyectosley.idproyectoley, " +
                " proyectosleydocumentos.fecha, proyectosley.nombre as nombreley, proyectosley.numeroboletin, count(resultados.idbusqueda) total_descargas,TO_CHAR(proyectosleydocumentos.fecha :: DATE, 'dd/mm/yyyy') as fechapub "+
                " from proyectosleydocumentos " +
                " left join proyectosley on proyectosleydocumentos.idproyectoley=proyectosley.idproyectoley " +
                " left join resultados on iddocumento=resultados.id and resultados.tipo='D' and resultados.picked='1' " +
                strWhere +
                " group by proyectosleydocumentos.iddocumento, proyectosleydocumentos.tipo, proyectosleydocumentos.titulo, proyectosley.numeroboletin, " +
                " proyectosleydocumentos.fecha, proyectosley.nombre, proyectosley.idproyectoley order by fecha desc") 
            #return cmd_sql
            df = pd.read_sql_query(cmd_sql, con=engine)   
            total_resultados = df.shape[0]
            for index, row in df.iterrows(): 
                 iddoc = row['iddocumento']
                 resultado += ("<div class='dvtbResultado'><table class='tbResultado'>"+                    
                    "<tr><td colspan='3' class='tbResultadoEpigrafe'>Tipo: {} • Boletín: {}</td></tr>"+
                    "<tr><th colspan='3'><a href='javascript:DescargarDocumento({}, {})'>{}</a></th></tr>     "+
                    "<tr><td colspan='3'>Referencia: {}</td></tr>"+
                    "<tr><td class='tbResultadoFecha'>Fecha publicación: {} &bull; Número de descargas <b>{}</b></td>"+                    
                    "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/prv.svg' alt='Previsualizar' onclick='javascript:VisualizarDocumento()' /></td>"+
                    "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/dwn.svg' alt='Descargar' onclick='javascript:DescargarDocumento({}, {})' /></td>"+
                    "</tr></table></div>").format(row['tipo'], row['numeroboletin'], str(row['iddocumento']), str(row['idproyectoley']), 
                                                  row['titulo'], row['nombreley'], row['fechapub'], str(row['total_descargas']),str(row['iddocumento']),str(row['idproyectoley']))            

            resultado = '<p><b>' + str(total_resultados) + '</b> documento(s) encontrado(s) con <br /><span class="qKotoba">'+ usrquery + '</span></p>|'+ resultado

        if cmd_busqueda == 'DESCARGARDOCUMENTO' :
            dictParams = crear_diccionario(parametros);
            #Registrar bd

            #URL descarga
            df = pd.read_sql_query('select archivo from proyectosleydocumentos where iddocumento='+dictParams['iddocumento'], con=engine)            
            for index, row in df.iterrows():
                nombre_doc = row['archivo']
            resultado = app_url + 'docs/' + dictParams['idley'] + '/' + urllib.parse.quote(nombre_doc)

        if cmd_busqueda == 'LISTARPROYECTOS' :
            cmd_sql = ("select proyectosley.idproyectoley,proyectosley.numeroboletin,proyectosley.tipoiniciativa,proyectosley.nombre as nombreproyecto,proyectosley.fechaingreso,"+
                "TO_CHAR(fechaingreso :: DATE, 'dd/mm/yyyy') as fecingreso,lower(materias.nombre) materia,count(resultados.idbusqueda) total_descargas from proyectosley " +
                " inner join proyectosleymaterias on proyectosley.idproyectoley=proyectosleymaterias.idproyectoley " +
                " inner join materias on proyectosleymaterias.idmateria=materias.idmateria " +
                " left join resultados on proyectosley.idproyectoley=resultados.id and resultados.tipo='P' and resultados.picked='1' " +
                " group by proyectosley.idproyectoley,proyectosley.numeroboletin,proyectosley.tipoiniciativa,proyectosley.nombre,proyectosley.fechaingreso, materias.nombre " +
                " order by proyectosley.fechaingreso desc limit 50")
            #return cmd_sql
            df = pd.read_sql_query(cmd_sql, con=engine)
            idproyecto = 0
            materias = ''            
            for index, row in df.iterrows():
                if idproyecto == 0 :
                  idproyecto = row['idproyectoley']
                  numeroboletin = row['numeroboletin']
                  tipoiniciativa = 'Mensaje'
                  if row['tipoiniciativa'] == '2' :
                      tipoiniciativa = 'Moción'
                  nombreproyecto = row['nombreproyecto']
                  fecingreso = row['fecingreso']
                  materias += row['materia'] + ', '
                  total_descargas = row['total_descargas']
                else :
                  if idproyecto != row['idproyectoley'] :
                      resultado += ("<div class='dvtbResultado'>"+
                            "<table class='tbResultado'>"+
                            "<tr><td colspan='2' class='tbResultadoEpigrafe'>Tipo iniciativa: {} &bull; Boletín: {}</td></tr>"+
                            "<tr><th colspan='2'><a href=\"javascript:VerProyecto('{}', {})\">{}</a></th></tr>"+
                            "<tr><td colspan='2' style='text-align:justify'>Materias: {}</td></tr>"+
                            "<tr><td class='tbResultadoFecha'>Fecha ingreso: {} &bull; Número de visitas: <b>{}</b></td>"+
                            "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Visitar' onclick=\"javascript:VerProyecto('{}', {})\" /></td></tr>"+
                            "</table></div>").format(tipoiniciativa, numeroboletin, nombreproyecto, idproyecto, nombreproyecto, materias[0:len(materias)-2]+'.', fecingreso, total_descargas, nombreproyecto, idproyecto)

                      idproyecto = row['idproyectoley']
                      numeroboletin = row['numeroboletin']
                      if row['tipoiniciativa'] == '2' :
                        tipoiniciativa = 'Moción'
                      nombreproyecto = row['nombreproyecto']
                      fecingreso = row['fecingreso']
                      materias += row['materia'] + ', '
                      total_descargas = row['total_descargas']
                  else :
                      materias += row['materia'] + ', '
            resultado += ("<div class='dvtbResultado'>"+
                    "<table class='tbResultado'>"+
                    "<tr><td colspan='2' class='tbResultadoEpigrafe'>Tipo iniciativa: {} &bull; Boletín: {}</td></tr>"+
                    "<tr><th colspan='2'><a href=\"javascript:VerProyecto('{}', {})\">{}</a></th></tr>"+
                    "<tr><td colspan='2' style='text-align:justify'>Materias: {}</td></tr>"+
                    "<tr><td class='tbResultadoFecha'>Fecha ingreso: {} &bull; Número de visitas: <b>{}</b></td>"+
                    "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Visitar' onclick=\"javascript:VerProyecto('{}', {})\" /></td></tr>"+
                    "</table></div>").format(tipoiniciativa, numeroboletin, nombreproyecto, idproyecto, nombreproyecto, materias[0:len(materias)-2]+'.', fecingreso, total_descargas, nombreproyecto, idproyecto)

        if cmd_busqueda == 'BUSCARPROYECTOS' :
            dictParams = crear_diccionario(parametros);
            criterio = dictParams['criterio']
            usrquery = dictParams['usrquery']

            strWhere = ''
            total_resultados = 0

            if criterio == 'E' :
                strWhere = 'where (upper(proyectosley.nombre)=\'' + usrquery.upper() + '\') '
            else :
                matquery = usrquery.split(' ')
                if criterio == 'A' :
                    matquery = quitar_stopwords(matquery)           
                strWhere = ''
                for m in matquery :
                    strWhere += (" (upper(proyectosley.nombre) like '%%%%" + m.upper() + "%%%%') or (upper(materias.nombre) like '%%%%" + m.upper() + "%%%%') or "+
                             "  (upper(proyectosley.numeroboletin) like '%%%%" + m.upper() + "%%%%') or ")                
                if strWhere != '':
                    strWhere = 'where ' + strWhere[0:len(strWhere)-4]
            
            idproyecto = 0
            materias = ''
            tipoiniciativa = ''
            nombreproyecto = ''
            numeroboletin = ''
            fecingreso = ''
            total_descargas = 0

            cmd_sql = ("select proyectosley.idproyectoley,proyectosley.numeroboletin,proyectosley.tipoiniciativa,proyectosley.nombre as nombreproyecto,proyectosley.fechaingreso,"+
                "TO_CHAR(fechaingreso :: DATE, 'dd/mm/yyyy') as fecingreso,lower(materias.nombre) materia,count(resultados.idbusqueda) total_descargas from proyectosley " +
                " inner join proyectosleymaterias on proyectosley.idproyectoley=proyectosleymaterias.idproyectoley " +
                " inner join materias on proyectosleymaterias.idmateria=materias.idmateria " +
                " left join resultados on proyectosley.idproyectoley=resultados.id and resultados.tipo='P' and resultados.picked='1' " +
                strWhere +
                " group by proyectosley.idproyectoley,proyectosley.numeroboletin,proyectosley.tipoiniciativa,proyectosley.nombre,proyectosley.fechaingreso, materias.nombre " +
                " order by proyectosley.fechaingreso desc")
            #return cmd_sql
            df = pd.read_sql_query(cmd_sql, con=engine)
            total_resultados = 0
            for index, row in df.iterrows():
                if idproyecto == 0 :
                  idproyecto = row['idproyectoley']
                  numeroboletin = row['numeroboletin']
                  tipoiniciativa = 'Mensaje'
                  if row['tipoiniciativa'] == '2' :
                      tipoiniciativa = 'Moción'
                  nombreproyecto = row['nombreproyecto']
                  fecingreso = row['fecingreso']
                  materias += row['materia'] + ', '
                  total_descargas = row['total_descargas']
                  total_resultados = total_resultados + 1 
                else :
                  if idproyecto != row['idproyectoley'] :
                      resultado += ("<div class='dvtbResultado'>"+
                            "<table class='tbResultado'>"+
                            "<tr><td colspan='2' class='tbResultadoEpigrafe'>Tipo iniciativa: {} &bull; Boletín: {}</td></tr>"+
                            "<tr><th colspan='2'><a href=\"javascript:VerProyecto('{}', {})\">{}</a></th></tr>"+
                            "<tr><td colspan='2' style='text-align:justify'>Materias: {}</td></tr>"+
                            "<tr><td class='tbResultadoFecha'>Fecha ingreso: {} &bull; Número de visitas: <b>{}</b></td>"+
                            "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Visitar' onclick=\"javascript:VerProyecto('{}', {})\" /></td></tr>"+
                            "</table></div>").format(tipoiniciativa, numeroboletin, nombreproyecto, idproyecto, nombreproyecto, materias[0:len(materias)-2]+'.', fecingreso, total_descargas, nombreproyecto, idproyecto)

                      idproyecto = row['idproyectoley']
                      numeroboletin = row['numeroboletin']
                      if row['tipoiniciativa'] == '2' :
                        tipoiniciativa = 'Moción'
                      nombreproyecto = row['nombreproyecto']
                      fecingreso = row['fecingreso']
                      materias += row['materia'] + ', '
                      total_descargas = row['total_descargas']
                      total_resultados = total_resultados + 1 
                  else :
                      materias += row['materia'] + ', '
            
            if total_resultados > 0 :
                resultado += ("<div class='dvtbResultado'>"+
                    "<table class='tbResultado'>"+
                    "<tr><td colspan='2' class='tbResultadoEpigrafe'>Tipo iniciativa: {} &bull; Boletín: {}</td></tr>"+
                    "<tr><th colspan='2'><a href=\"javascript:VerProyecto('{}', {})\">{}</a></th></tr>"+
                    "<tr><td colspan='2' style='text-align:justify'>Materias: {}</td></tr>"+
                    "<tr><td class='tbResultadoFecha'>Fecha ingreso: {} &bull; Número de visitas: <b>{}</b></td>"+
                    "<td class='tbResultadoDescargar'><img class='imgDwn' src='imgs/visitar.svg' alt='Visitar' onclick=\"javascript:VerProyecto('{}', {})\" /></td></tr>"+
                    "</table></div>").format(tipoiniciativa, numeroboletin, nombreproyecto, idproyecto, nombreproyecto, materias[0:len(materias)-2]+'.', fecingreso, total_descargas, nombreproyecto, idproyecto)                        

            resultado = '<p><b>' + str(total_resultados) + '</b> proyecto(s) encontrado(s) con <span class="qKotoba">'+ usrquery + '</span></p>|'+ resultado

        if cmd_busqueda == 'BUSCARPROYECTO' :
            dictParams = crear_diccionario(parametros);
            idproyecto = dictParams['idproyecto']
            idcomision = 0
            nombrecomision = ''
            materias = ''
            integrantes = ''
            numeroboletin = ''
            tipoiniciativa = ''
            nombreproyecto = ''
            fecingreso = ''
            total_descargas = 0

            cmd_sql = ("select proyectosley.idproyectoley,proyectosley.numeroboletin,proyectosley.tipoiniciativa,proyectosley.nombre as nombreproyecto,proyectosley.fechaingreso,proyectosley.idcomision, "+
                "TO_CHAR(fechaingreso :: DATE, 'dd/mm/yyyy') as fecingreso,lower(materias.nombre) materia,count(resultados.idbusqueda) total_descargas from proyectosley " +
                " inner join proyectosleymaterias on proyectosley.idproyectoley=proyectosleymaterias.idproyectoley " +
                " inner join materias on proyectosleymaterias.idmateria=materias.idmateria " +
                " left join resultados on proyectosley.idproyectoley=resultados.id and resultados.tipo='P' and resultados.picked='1' " +
                " where (proyectosley.idproyectoley=" + str(idproyecto) + ") " +
                " group by proyectosley.idproyectoley,proyectosley.numeroboletin,proyectosley.tipoiniciativa,proyectosley.nombre,proyectosley.fechaingreso, materias.nombre,proyectosley.idcomision " +
                " order by proyectosley.fechaingreso desc")
            #return cmd_sql
            df = pd.read_sql_query(cmd_sql, con=engine)
            for index, row in df.iterrows():  
                  idcomision = row['idcomision']
                  numeroboletin = row['numeroboletin']
                  tipoiniciativa = 'Mensaje'
                  if row['tipoiniciativa'] == '2' :
                      tipoiniciativa = 'Moción'
                  nombreproyecto = row['nombreproyecto']
                  fecingreso = row['fecingreso']
                  materias += row['materia'] + ', '
                  total_descargas = row['total_descargas']
                  
            resultado = numeroboletin + '|' + tipoiniciativa + '|' + nombreproyecto + '|' +  fecingreso + '|' + str(total_descargas) + '|' + materias[0:len(materias)-2] + '|' + str(idcomision) + '|'
            
            cmd_sql = ("select comisiones.nombre, diputados.iddiputado, CONCAT(diputados.nombre,' ',diputados.apellidopaterno) as nombre_diputado, diputadosperiodo.distrito, " +
                   " CONCAT(upper(diputados.nombre),'-',upper(diputados.apellidopaterno)) as nombre_url " +
                   " from comisiones " +
                   " left join integrantescomision on comisiones.idcomision=integrantescomision.idcomision " +
                   " left join diputados on integrantescomision.iddiputado=diputados.iddiputado " +
                   " left join diputadosperiodo on diputados.iddiputado=diputadosperiodo.iddiputado " +
                   " where comisiones.idcomision="+str(idcomision))
            #return cmd_sql
            df = pd.read_sql_query(cmd_sql, con=engine)           
            for index, row in df.iterrows():                 
                 if row['nombre_diputado'] != ' ' :
                     nombrecomision = row['nombre']
                     integrantes += ("<div class='card-small'>" +
                        "<img src='imgs/legisladores/img-{}.jpg'  onclick=\"VerLegislador('{}','{}')\" />" +
                        "<p>{}<br /><span>Diputado D{}</span></p>" +                       
                        "</div>").format(str(row['iddiputado']), row['nombre_url'],  str(row['iddiputado']), row['nombre_diputado'], str(row['distrito']))
                 else :
                     integrantes = '<div id=\"dvSinAtencedentes\">Sin antecedentes</div>'
            resultado += nombrecomision + '|' + nombrecomision.replace(' ', '-').upper() + '|' + integrantes + '|' + str(idproyecto)

        if cmd_busqueda == 'DOCUMENTOSPROYECTOLEY' :
            dictParams = crear_diccionario(parametros);
            idproyecto = dictParams['idproyecto']
            cmd_sql = ("select proyectosleydocumentos.iddocumento, proyectosleydocumentos.tipo, proyectosleydocumentos.titulo, proyectosley.idproyectoley, " +
                " proyectosleydocumentos.fecha, proyectosley.nombre as nombreley, proyectosley.numeroboletin, count(resultados.idbusqueda) total_descargas,TO_CHAR(proyectosleydocumentos.fecha :: DATE, 'dd/mm/yyyy') as fechapub "+
                " from proyectosleydocumentos " +
                " left join proyectosley on proyectosleydocumentos.idproyectoley=proyectosley.idproyectoley " +
                " left join resultados on iddocumento=resultados.id and resultados.tipo='D' and resultados.picked='1' " +
                " WHERE (proyectosleydocumentos.idproyectoley=" + str(idproyecto) + ") " +
                " group by proyectosleydocumentos.iddocumento, proyectosleydocumentos.tipo, proyectosleydocumentos.titulo, proyectosley.numeroboletin, " +
                " proyectosleydocumentos.fecha, proyectosley.nombre, proyectosley.idproyectoley order by fecha desc limit 2")             
            df = pd.read_sql_query(cmd_sql, con=engine)
            if df.shape[0] == 0 :
                resultado = '<div id=\"dvSinAtencedentes\">No se registran documentos</div>'               
            else :
                for index, row in df.iterrows():
                    resultado += ("<div class='dvInfo dvDocLey'>"+
                    "<table class='tbResultado tb2'>"+
                    "<tr><td colspan='2' class='tbResultadoEpigrafe'>Tipo: {} &bull; Nro Boletín: {}</td></tr>" +
                    "<tr><th colspan='2'><a href=\"javascript:DescargarDocumento({}, {})\" style='font-size:0.7em'>{}</a></th></tr>" +
                    "<tr><td class='tbResultadoFecha'>Fecha publicación: {} • Número de descargas <b>{}</b></td>" +
                    "<td class='tbResultadoDescargar'>"+
                    "<img class='imgDwn' src='imgs/dwn.svg' style='width:95px' alt='Descargar' onclick=\"javascript:DescargarDocumento({}, {})\" /></td></tr>"+                    
                    "</table></div>").format(row['tipo'], row['numeroboletin'], str(row['iddocumento']), str(row['idproyectoley']), row['titulo'], row['fechapub'], str(row['total_descargas']),str(row['iddocumento']),  str(row['idproyectoley']))                                
            
    except Exception as e:
        print('Error al procesar request ' + cmd_busqueda + ' ('+str(e)+')') 

    return resultado

def quitar_stopwords(lista) :
    lista_sw = ['a','acaso','acerca','además','ah','ahí','ahora','al','algo','allí','alrededor','anteayer','antes','aparte','aquel','aquella','aquellas','aquello','aquellos','aquí','así','asimismo','aun',             'aún','ay','ayer','bastante','bien','cada','casi','cerca','como','cómo','con','cual','cuál','cuales','cuáles','cuando','cuándo','cuanta','cuantas','cuanto','cuantos','cuya','cuyas','cuyo','cuyos','de',                'debajo','debe','del','delante','demasiado','dentro','deprisa','despacio','después','detrás','donde','dónde','e','el','él','ella','ellas','ellos','en','encima','entre','es','esa','esas','ese','eso',                'esos','esta','estas','este','esto','estos','fuera','ha','hacer','hay','hoy','incluso','ja','jamás','je','ji','la','las','le','lejos','les','lo','los','luego','mal','mas','más','me','medio','menos',                'mi','mí','mía','mías','mío','míos','mucho','muy','nada','ni','no','nos','nosotras','nosotros','nuestra','nuestras','nuestro','nuestros','nunca','o','os','para','pero','poco','por','pronto','puede',                'que','qué','quien','quién','quienes','quiénes','quieren','quizá','quizás','se','ser','si','sí','sin','sobre','sólo','son','su','sus','suya','suyas','suyo','suyos','tal','también','tampoco','tan',                'tarde','te','temprano','ti','tienen','todas','todavía','todo','tu','tú','tuya','tuyas','tuyo','tuyos','u','uf','un','una','unas','unos','usted','ustedes','va','vos','vosotras','vosotros','vuestra',                'vuestras','vuestro','vuestros','y','ya','yo']
    for sw in lista_sw :
        if sw in lista :
            lista.remove(sw)
    return lista

def crear_diccionario(parametros) :
    dictParams = {}
    listParams = parametros.split('|');
    for param in listParams: 
        if param != '' :
            p = param.split(':')
            dictParams[p[0]] = p[1]
    return dictParams

def iniciar_ajax():
    print("Content-Type: text/plain; charset=iso-8859-1\n")
    #sesion_id = comprobar_sesion()       
    #print('sesion_id:' + str(sesion_id))

    try:
        # Resultado
        cmd = form["cmd"].value
        params = form["params"].value
        resultado = ejecutar_busqueda(cmd, params)
        print(resultado)

    except Exception as e:
        print('Error al procesar request ('+str(e)+')')          
    
iniciar_ajax()