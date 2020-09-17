var opcionesbusquedas = [];
var interfazActual = '';

function GetXmlHttpObject() {
	if (window.XMLHttpRequest)
	  return new XMLHttpRequest();	
	if (window.ActiveXObject)
		return new ActiveXObject("Microsoft.XMLHTTP");
	return null;
}

function Buscador(cmd, params) {
    if (cmd != '' && params != null) {

        //Iniciar buscando
        if (document.getElementById('usrQueryautocomplete-list'))
            document.getElementById('usrQueryautocomplete-list').style.display = 'none';
        document.getElementById('dvCargando').style.display = 'block';
        document.body.style.cursor = 'wait';
        var xmlhttp = GetXmlHttpObject();

        if (xmlhttp == null) {
            alert("Su navegador no soporta Ajax");
            return;
        } else {
            url = "ajax.py";
            url = url + "?cmd=" + cmd + "&params=" + setParams(params);
            console.log(url)
            xmlhttp.open("GET", url, true);
            xmlhttp.onreadystatechange = function () {
                if (xmlhttp.readyState === xmlhttp.DONE && xmlhttp.status === 200) {
                    var resultado = xmlhttp.responseText;
                    //console.log(resultado);
                    switch (cmd) {
                        case 'BUSCARINDEX':
                            matData = resultado.split('|');
                            document.getElementById('dvResultado').innerHTML = matData[0];                          
                            if (matData[2] == 0)
                                document.getElementById('txResultado').innerHTML = '<p>NO se encontraron resultados con <br /><span class="qKotoba">' + matData[1] + '</span>.<br />Recomendamos utilizar la b&uacute;squeda avanzada.</p>';
                            else {
                                document.getElementById('Pagebody').style.backgroundColor = '#efefef';
                                document.getElementById('txResultado').innerHTML = '<p><b>' + matData[2] + '</b> resultado(s) encontrado(s) con <span class="qKotoba">' + matData[1] + '</span>.</p>';
                            }
                            document.getElementById('dvInicio').style.visibility = 'hidden';
                            document.getElementById('dvInicio').style.position = 'absolute';

                            document.getElementById('txResultado').style.visibility = 'visible'; 
                            document.getElementById('dvResultado').style.visibility = 'visible';
                            break;

                        case 'LISTARLEGISLADORES':
                            document.getElementById('dvResultado').innerHTML = resultado;
                            ExtraerLegisladores();
                            autocomplete(document.getElementById("usrQuery"), opcionesbusquedas);
                            break;

                        case 'BUSCARLEGISLADORES':
                            document.getElementById('dvResultado').innerHTML = resultado;
                            break;

                        case 'BUSCARLEGISLADOR':
                            matData = resultado.split('|');
                            document.getElementById('imgLegislador').src = 'imgs/legisladores/img-' + matData[0] + '.jpg';
                            document.getElementById('spNombre').innerText = matData[1] + ' ' + matData[2];
                            document.getElementById('pAntecendetes').innerHTML = '<span>Comunas:</span> ' + matData[9] + '<br />' +
                                '<span>Distrito:</span> Nro ' + matData[7] + '<br />' +
                                '<span>Regi&oacute;n:</span> ' + matData[8] + '<br />' +
                                '<span>Per&iacute;odo:</span> 2018 - 2022<br />' +
                                '<span>Partido:</span> ' + matData[6];
                            document.getElementById('aTelefono').href = 'tel:' + matData[3];
                            document.getElementById('aTelefono').innerHTML = matData[3];
                            document.getElementById('aEmail').href = 'mailto:' + matData[4];
                            document.getElementById('aEmail').innerHTML = matData[4];
                            document.getElementById('aTwitter').href = 'https://www.twitter.com/' + matData[5];
                            document.getElementById('aTwitter').innerHTML = matData[5];
                            document.getElementById('ulComisiones').innerHTML = matData[10];
                            document.getElementById('dvResultado').style.visibility = 'visible';
                            break;

                        case 'LISTARCOMISIONES':
                            matData = resultado.split('|');
                            document.getElementById('dvResultado').innerHTML = matData[0];
                            document.getElementById('txResultado').innerHTML = '<p>Actualmente existen <b>' + matData[1]+'</b> comisiones activas.</p>';
                            ExtraerComisiones();
                            autocomplete(document.getElementById("usrQuery"), opcionesbusquedas);
                            break;

                        case 'BUSCARCOMISIONES':
                            matData = resultado.split('|');
                            document.getElementById('dvResultado').innerHTML = matData[0];
                            document.getElementById('txResultado').innerHTML = '<p>Actualmente existen <b>' + matData[1] + '</b> comisiones activas.</p>';
                            break;

                        case 'BUSCARCOMISION':
                            matData = resultado.split('|');

                            document.getElementById('spNombre').innerText = matData[0];
                            document.getElementById('aTelefono').href = 'tel:' + matData[1];
                            document.getElementById('aTelefono').innerHTML = matData[1];
                            document.getElementById('aEmail').href = 'mailto:' + matData[2];
                            document.getElementById('aEmail').innerHTML = matData[2];

                            document.getElementById('dvIntegrantes').innerHTML = matData[3];
                            document.getElementById('ulProyectos').innerHTML = matData[4];

                            document.getElementById('dvResultado').style.visibility = 'visible';
                            break;

                        case 'BUSCARDOCUMENTOS':
                            matRes = resultado.split('|');
                            document.getElementById('txResultado').innerHTML = matRes[0];
                            document.getElementById('dvResultado').innerHTML = matRes[1];
                            break;

                        case 'LISTARDOCUMENTOS':
                            document.getElementById('dvResultado').innerHTML = resultado;
                            ExtraerDocumentos();
                            autocomplete(document.getElementById("usrQuery"), opcionesbusquedas);
                            break;

                        case 'DESCARGARDOCUMENTO':
                            window.open(resultado);
                            break;

                        case 'LISTARPROYECTOS':
                            document.getElementById('dvResultado').innerHTML = resultado;
                            ExtraerProyectos();
                            autocomplete(document.getElementById("usrQuery"), opcionesbusquedas);
                            break;

                        case 'BUSCARPROYECTOS':
                            matRes = resultado.split('|');
                            document.getElementById('txResultado').innerHTML = matRes[0];
                            document.getElementById('dvResultado').innerHTML = matRes[1];
                            break;

                        case 'BUSCARPROYECTO':
                            try {
                                matRes = resultado.split('|');
                                document.getElementById('spNombre').innerHTML = matRes[2];
                                document.getElementById('dvAntencedentes').innerHTML = '<p><b>Antecedentes generales</b>' +
                                    '<br /> <span>Bolet&iacute;n: ' + matRes[0] + '</span>' +
                                    '<br /> <span>Iniciativa: ' + matRes[1] + '</span>' +
                                    '<br /> <span>Fecha ingreso: ' + matRes[3] + '</span>' +
                                    '</p>';
                                document.getElementById('dvMaterias').innerHTML = '<p><b>Materias</b><br /> <span>' + matRes[5] + '</span>';
                                matDate = matRes[3].split('/');
                                document.getElementById('dvFechaIng').innerHTML = matRes[3];
                                var diff = Math.abs(new Date() - new Date(matDate[2], matDate[1], matDate[0]));
                                document.getElementById('dvFechaDif').innerHTML = '(tiempo transcurrido ' + parseInt(diff / (1000 * 60 * 60 * 24)) + ' d&iacute;as)';
                                document.getElementById('lnkComision').innerHTML = matRes[7];
                                document.getElementById('lnkComision').href = "javascript: VerComision('" + matRes[8] + "', '" + matRes[6] + "')";
                                document.getElementById('dvIntegrantes').innerHTML = matRes[9];
                                BuscarDocsProyecto(matRes[10]);
                            } catch (e) {
                                console.log(resultado);
                            }
                            break;

                        case 'DOCUMENTOSPROYECTOLEY':                           
                            document.getElementById('dvDocs').innerHTML = '<p><b>Documentos</b>' + resultado;                            
                            document.getElementById('dvIzq').style.visibility = 'visible';
                            document.getElementById('dvDer').style.visibility = 'visible';
                            break;
                    }
                    //Terminar buscando
                    document.getElementById('dvCargando').style.display = 'none';
                    document.body.style.cursor = 'default';
                }
            }
            xmlhttp.send(null);
        }
    }
}

function IniciarLegisladores() {
    Buscador('LISTARLEGISLADORES', '');    
}

function IniciarComisiones() {
    Buscador('LISTARCOMISIONES', '');
}

function IniciarDocumentos() {
    Buscador('LISTARDOCUMENTOS', '');
}

function IniciarProyectos() {
    Buscador('LISTARPROYECTOS', '');
}

function ExtraerLegisladores() {
    var legisladores = document.getElementsByClassName('card');
    for (x = 0; x < legisladores.length; x++) {
        opcionesbusquedas.push(legisladores[x].getElementsByTagName('h1')[0].innerText);
    }
}

function ExtraerComisiones() {
    var comisiones = document.getElementsByClassName('tbResultado');
    for (x = 0; x < comisiones.length; x++) {        
        opcionesbusquedas.push(comisiones[x].getElementsByTagName('a')[0].innerText);
    }
}

function ExtraerDocumentos() {
    var documentos = document.getElementsByClassName('tbResultado');
    for (x = 0; x < documentos.length; x++) {
        opcionesbusquedas.push(documentos[x].getElementsByTagName('a')[0].innerText);
    }
}

function ExtraerProyectos() {
    var documentos = document.getElementsByClassName('tbResultado');
    for (x = 0; x < documentos.length; x++) {
        opcionesbusquedas.push(documentos[x].getElementsByTagName('a')[0].innerText);
    }
}

function VerLegislador(nombre, id) {
    location.href = 'legislador.htm?diputado=' + encodeURI(nombre) + '&id=' + id;
}

function VerComision(nombre, id) {
    location.href = 'comision.htm?comision=' + encodeURI(nombre) + '&id=' + id;
}

function VerProyecto(nombre, id) {
    location.href = 'proyecto.htm?proyecto=' + encodeURI(nombre) + '&id=' + id;
}

function BuscarLegislador(iddiputado) {
    params = { 'iddiputado': iddiputado }
    Buscador('BUSCARLEGISLADOR', params);    
}

function BuscarProyecto(idproyecto) {
    params = { 'idproyecto': idproyecto }
    Buscador('BUSCARPROYECTO', params);
}

function BuscarDocsProyecto(idproyecto) {
    params = { 'idproyecto': idproyecto }
    Buscador('DOCUMENTOSPROYECTOLEY', params);
}

function BuscarComision(idcomision) {
    params = { 'idcomision': idcomision }
    Buscador('BUSCARCOMISION', params);
}

function DescargarDocumento(iddocumento, idley) {    
    params = { 'iddocumento': iddocumento, 'idley': idley }
    Buscador('DESCARGARDOCUMENTO', params);
}

function VisualizarDocumento() {
    document.getElementById('dvPrevisualizar').style.display = 'block';
}

function setParams(params) {
    if (params == '')
        return '0';
    else {
        strParams = '';
        for (const [key, value] of Object.entries(params)) {
            strParams += key + ":" + value + "|";
        }
    }
    return strParams;
}

function findGetParameter(parameterName) {
    var result = null,
        tmp = [];
    var items = location.search.substr(1).split("&");
    for (var index = 0; index < items.length; index++) {
        tmp = items[index].split("=");
        if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
    }
    return result;
}

function IniciarInterfaz(){
	var searchInput = document.getElementById('usrQuery'); 
	IniciarBarraSuperior();	
	IniciarEventoQuery(searchInput);
	IniciarEventoBtnBuscador();
	
	searchInput.focus();
}

function IniciarBarraSuperior() {
    var matURL = window.location.href.split('/');
    var urlActual = matURL[matURL.length - 1].split('.htm')[0];
    interfazActual = urlActual;
    //console.log(urlActual);
    if (urlActual == '' || urlActual == null) {
        urlActual = 'index';       
    }
    if (urlActual == 'proyectos')
        urlActual = 'proyecto';
    if (urlActual == 'documentos')
        urlActual = 'documento';
    if (urlActual == 'comisiones')
        urlActual = 'comision';
    if (urlActual == 'legisladores')
        urlActual = 'legislador';

    if (urlActual == 'index')
        document.getElementById('Pagebody').style.backgroundColor = '#ffffff';

    console.log(urlActual);
    try {
        document.getElementById('lnk-' + urlActual).classList.add("active");
    } catch (e) {
        console.log('Error: ' + e);
    }
}

function IniciarEventoQuery(searchInput) {
    searchInput.addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            ValidarBusqueda(searchInput.value);
        }
    });
}

function IniciarEventoBtnBuscador(){
	document.addEventListener('DOMContentLoaded', function() {
		var box = document.getElementsByClassName('box')[0],
			button = document.getElementsByClassName('button')[0];
	
		button.addEventListener('click', function(e) {
			if (box.classList.contains('box-hidden')) {
				// show
				box.classList.add('box-transition');
				box.clientWidth; // force layout to ensure the now display: block and opacity: 0 values are taken into account when the CSS transition starts.
				box.classList.remove('box-hidden');
                document.getElementById("imgBusquedaAvanzada").src = 'imgs/ba-2.svg';                
                document.getElementById('usrQueryAdv').value = document.getElementById('usrQuery').value;
			} else {
				// hide
				box.classList.add('box-transition');
				box.classList.add('box-hidden');
				document.getElementById("imgBusquedaAvanzada").src = 'imgs/ba.svg';
			}
		}, false);
	
		box.addEventListener('transitionend', function() {
			box.classList.remove('box-transition');
		}, false);
	});
}

function ValidarBusqueda(strQuery) {
    if (strQuery.length > 2) {
        var criterio = 'T';
        if (document.getElementById('criterioA').checked)
            criterio = 'A';
        if (document.getElementById('criterioE').checked)
            criterio = 'E';
        params = { 'usrquery': strQuery, 'criterio': criterio };
        Buscador('BUSCAR' + interfazActual.toUpperCase(), params);
        console.log(strQuery + ' ' + interfazActual);
    } else {
        Swal.fire(
            'Error',
            'Ingrese un valor ',
            'error')
    }
}

function Buscar(strQuery){	
    ValidarBusqueda(strQuery);
}

function includeHTML() {
    var z, i, elmnt, file, xhttp;
    /* Loop through a collection of all HTML elements: */
    z = document.getElementsByTagName("*");
    for (i = 0; i < z.length; i++) {
        elmnt = z[i];
        /*search for elements with a certain atrribute:*/
        file = elmnt.getAttribute("w3-include-html");
        if (file) {
            /* Make an HTTP request using the attribute value as the file name: */
            xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function () {
                if (this.readyState == 4) {
                    if (this.status == 200) { elmnt.innerHTML = this.responseText; }
                    if (this.status == 404) { elmnt.innerHTML = "Page not found."; }
                    /* Remove the attribute, and call this function once more: */
                    elmnt.removeAttribute("w3-include-html");
                    includeHTML();
                }
            }
            xhttp.open("GET", file, true);
            xhttp.send();
            /* Exit the function: */
            return;
        }
    }
}