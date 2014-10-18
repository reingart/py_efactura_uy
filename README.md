py_efactura_uy
==============

Electronic Invoice implementation for DGI (Uruguay) via WebServices

Requerimientos / Requeriments:
------------------------------

 * La implementación de xmlsec es ad-hoc desarrollada en python (usando M2Crypto: bindings para OpenSSL).
 * Se usa lxml opcionalmente, ya que si no está disponible se hace canonicalizacion por python
 * No depender de libxml2 ni libxmlsec que parecen más trabajosas y medio antiguas.
 * Es necesario instalar la biblioteca [pysimplesoap](https://code.google.com/p/pysimplesoap/) y se recomienda httplib2 para un mejor manejo de las conexiones HTTP.

Instalación / install
---------------------

GNU/Linux (Debian, Ubuntu, etc.):
```
sudo apt-get install python-m2crypto python-lxml python-httplib2
```

Windows:
 * M2Crypto-0.21.1-openssl-1.0.1e-py2.7-win32.zip o similar
 * 

Instalar la versión de desarrollo de pysimplesoap (que tiene soporte para cdata, xmlsec y c14n), directamente del repositorio:

 * Bajar https://pysimplesoap.googlecode.com/archive/default.zip
 * Descomprimir
 * Ejecutar `python setup.py`

Estado / status:
-----------------

La idea es utilizar las bibliotecas (y "lecciones aprendidas") desarrolladas para el proyecto de factura electrónica en Argentina, pyafipws:

https://code.google.com/p/pyafipws/

Principalmente se adaptó la librería pysimplesoap para todo el tema de WS Security (firma y validación).
Se busca una funcionalidad ad-hoc con pocas dependencias y simple de mantener.

Prácticamente es puro-python (solo requeriría tener los bindings para OpenSSL: M2Crypto, aunque se podría llegar a ejecutar el comando externamente), por lo que funcionaría tanto en Java vía Jython y en .NET vía IronPython.
También se podría usar desde lenguajes legados vía interfaz COM en Windows, y en general se manejaría todo por tipos de datos simples (que se podrían mapear a JSON, archivos de intercambio de texto tipo Cobol y tablas DBF para xBase y similares).

Por el momento estaría funcionando la presentación del CFE en pruebas:

 * Arma el requerimiento base (usando un CFE de muestra que está en el manual de DGI)
 * Utiliza los certificados para el tema de la firma del mensaje.
 * Agrega los headers WSSE (firmado). 
 * Envia el requerimiento al webservice de DGI
 * Recibe la respuesta
 * Valida los encabezados de seguridad en respuesta (WSSE), para asegurarse  que la constestación viene firmada por una CA válida (CorreoUruguayoCA.crt)

Por el momento usa un mensaje crudo (raw request), o sea, usa los objetos SimpleXmlElement y no parsea el WSDL (no tiene mucho sentido porque el método tiene un solo parámetro que es del tipo texto: CFE en xml).

La próxima etapa sería armar el CFE, pero podría hacerse también con SimpleXMLElement que simplifica el manejo de XML (inspirado por una extensión similar de PHP), por ej:
```
cfe = SimpleXMLElement()
cfe.marshal( ...
    {"eTck": {
            "TmstFirma": "2012-02-08T09:48:51Z",
            "Encabezado": {
                "IdDoc": {
                    "TipoCFE": 101,
                    "Serie": "A",
                    "Nro": 1,
                    "FchEmis": "2011-11-08",
                    "FmaPago": 1,
               }
          }        
     }
```
En este caso no se utilizaría los esquemas por lo que es mucho más flexible y no genera kilobytes de artefactos/codigo.
En Argentina nos sirvió bastante para no tener que regenerar todas las clases cuando hay una modificacion en los esquemas.
Además, permite abstraerse un poco de la jerarquia de la organización, por ej para PyAfipWs exponemos componentes que arman internamente los diccionarios y luegos lo serializan.
Al no exponer las clases se baja el acoplamiento, facilita la lógica y sobre todo, es compatible con sistemas legados que no manejan tan bien objetos.

Pueden ver un ejemplo para el webservice WSMTXCA:

https://github.com/reingart/pyafipws/blob/master/wsmtx.py

Fijense que CrearFactura, AgregarIVA, AgregarItem van creando el diccionario interno, y recien en AutorizarComprobante se rearma la estructura del diccionario que pide AFIP y serializa a xml
Como podrán ver, no hay mucha lógica más que controlar los campos nulos o aquellos que deben o no enviarse dependiendo de cierto tipo de datos.

Ejemplo / example:
------------------

```
reingart@s5ultra:~/py_efactura_uy$ python prueba.py
INFO:pysimplesoap.client:POST https://efactura.dgi.gub.uy:6443/ePrueba/ws_eprueba
DEBUG:pysimplesoap.client:SOAPAction: "http://dgi.gub.uyaction/AWS_EFACTURA.EFACRECEPCIONSOBRE"
Content-length: 11222
Content-type: text/xml; charset="UTF-8"
DEBUG:pysimplesoap.client:
<?xml version="1.0" encoding="UTF-8"?><DGICFE:EnvioCFE version="1.0" xmlns:DGICFE="http://cfe.dgi.gub.uy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://cfe.dgi.gub.uy EnvioCFE_v1.11.xsd">
    <DGICFE:Caratula version="1.0">
        <DGICFE:RutReceptor>214844360018</DGICFE:RutReceptor>
        <DGICFE:RUCEmisor>160010030018</DGICFE:RUCEmisor>
        <DGICFE:Idemisor>3009</DGICFE:Idemisor>
        <DGICFE:CantCFE>1</DGICFE:CantCFE>
    <DGICFE:Fecha>2014-10-18T14:14:12-03:00</DGICFE:Fecha><DGICFE:X509Certificate>MIIFjTCCA3WgAwIBAgIQMQXIJY3LXBdT8m...
</DGICFE:X509Certificate></DGICFE:Caratula>
    <ns0:CFE version="1.0" xmlns:ns0="http://cfe.dgi.gub.uy">
        <ns0:eTck>
            <ns0:TmstFirma>2012-02-08T09:48:51Z</ns0:TmstFirma>
            <ns0:Encabezado>
                <ns0:IdDoc>
                    <ns0:TipoCFE>101</ns0:TipoCFE>
                    <ns0:Serie>A</ns0:Serie>
                    <ns0:Nro>1</ns0:Nro>
                    <ns0:FchEmis>2011-11-08</ns0:FchEmis>
                    <ns0:FmaPago>1</ns0:FmaPago>
                </ns0:IdDoc>
                <ns0:Emisor>
                    <ns0:RUCEmisor>160010030018</ns0:RUCEmisor>
                    <ns0:RznSoc>DGI-PRUEBA SERVICIOS WEB</ns0:RznSoc>
                    <ns0:CdgDGISucur>1</ns0:CdgDGISucur>
                    <ns0:DomFiscal>FERNANDEZ CRESPO AVDA. DANIEL 1534</ns0:DomFiscal>
                    <ns0:Ciudad>MONTEVIDEO</ns0:Ciudad>
                    <ns0:Departamento>MONTEVIDEO</ns0:Departamento>
                </ns0:Emisor>
                <ns0:Totales>
                    <ns0:TpoMoneda>UYU</ns0:TpoMoneda>
                    <ns0:MntTotal>5280</ns0:MntTotal>
                    <ns0:CantLinDet>3</ns0:CantLinDet>
                    <ns0:MntPagar>5280</ns0:MntPagar>
                </ns0:Totales>
            </ns0:Encabezado>
            <ns0:Detalle>
                <ns0:Item>
                    <ns0:NroLinDet>1</ns0:NroLinDet>
                    <ns0:IndFact>3</ns0:IndFact>
                    <ns0:NomItem>aaa</ns0:NomItem>
                    <ns0:Cantidad>20</ns0:Cantidad>
                    <ns0:UniMed>KG</ns0:UniMed>
                    <ns0:PrecioUnitario>230</ns0:PrecioUnitario>
                    <ns0:MontoItem>4600</ns0:MontoItem>
                </ns0:Item>
                <ns0:Item>
                    ...
                </ns0:Item>
            </ns0:Detalle>
            <ns0:CAEData>
                <ns0:CAE_ID>90110001945</ns0:CAE_ID>
                <ns0:DNro>1</ns0:DNro>
                <ns0:HNro>100</ns0:HNro>
                <ns0:FecVenc>2013-11-07</ns0:FecVenc>
            </ns0:CAEData>
        </ns0:eTck>
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
<SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#" xmlns:DGICFE="http://cfe.dgi.gub.uy" xmlns:ns0="http://cfe.dgi.gub.uy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
  <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
  <Reference URI="">
    <Transforms>
       <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
       <Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
    </Transforms>
    <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
    <DigestValue>MMjfRo/ni4gRbKqsqr03bRcZz0I=</DigestValue>
  </Reference>
</SignedInfo>
<SignatureValue>iPCP1IGdL+n3/8bESQpn2WUY1VYotLOeyqz0DBdXnXGvR46ofLwyOfRLOsyRMgVQVZn7VffZb2zy12/+UK2LYMNO7No7sD0iFIoCubXZRe59dFOh4eJga/SkwbScAEQJ40/Xjgabcurhj0DGmoVxFeIzmUiGdlpMlCb0Wcim2IE=</SignatureValue>

<KeyInfo>
    <X509Data>
        <X509IssuerSerial>
            <X509IssuerName>C=UY, O=ADMINISTRACION NACIONAL DE CORREOS, OU=SERVICIOS ELECTRONICOS, CN=Correo Uruguayo - CA</X509IssuerName>
            <X509SerialNumber>65162192734999528486526452739173670710</X509SerialNumber>
        </X509IssuerSerial>
    </X509Data>
</KeyInfo>

</Signature></ns0:CFE>
</DGICFE:EnvioCFE>

DEBUG:pysimplesoap.client:status: 200
x-client-ip: 190.50.167.167
content-language: en-US
x-backside-transport: OK OK
transfer-encoding: chunked
set-cookie: JSESSIONID=0000cggWpfP...:-1; Path=/wseprueba
expires: Sat, 18 Oct 2014 17:14:11 GMT
server: IBM_HTTP_Server
last-modified: Sat, 18 Oct 2014 17:14:11 GMT
connection: Keep-Alive
pragma: no-cache
cache-control: max-age=0, no-cache, no-store, must-revalidate
date: Sat, 18 Oct 2014 17:14:11 GMT
content-type: text/xml

<?xml version="1.0" encoding="UTF-8"?>
<ACKSobre xmlns="http://cfe.dgi.gub.uy" version="1.0"><Caratula><RUCReceptor>214844360018</RUCReceptor><RUCEmisor>160010030018</RUCEmisor><IDRespuesta>4653588</IDRespuesta><NomArch/><FecHRecibido>2014-10-18T15:14:12-02:00</FecHRecibido><IDEmisor>3009</IDEmisor><IDReceptor>4653588</IDReceptor><CantidadCFE>1</CantidadCFE><Tmst>2014-10-18T15:14:50-02:00</Tmst></Caratula><Detalle><Estado>AS</Estado><ParamConsulta><Token>SgPU4KtHBLDY5Hn6Q...</Token><Fechahora>2014-10-18T15:19:50-02:00</Fechahora></ParamConsulta></Detalle><Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
<SignedInfo>
  <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
  <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
  <Reference URI="">
    <Transforms>
      <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
      <Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
    </Transforms>
    <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
    <DigestValue>QeTeiLzCsxeToFRJI2CIGTgQovY=</DigestValue>
  </Reference>
</SignedInfo>
    <SignatureValue>YuZ2lnMHDae4wu6q4GVp6smIwZSGHP...=</SignatureValue><KeyInfo><X509Data><X509Certificate>MIIF2TCCA8GgAwIBAgIQGA6oKNh5KNJTDMMWaR...59izKA==</X509Certificate><X509IssuerSerial><X509IssuerName>CN=Correo Uruguayo - CA, OU=SERVICIOS ELECTRONICOS, O=ADMINISTRACION NACIONAL DE CORREOS, C=UY</X509IssuerName><X509SerialNumber>31977574735792617507739371020706040120</X509SerialNumber></X509IssuerSerial></X509Data></KeyInfo></Signature></ACKSobre>

214844360018
160010030018
4653588

2014-10-18T15:14:12-02:00
3009
4653588
1
2014-10-18T15:14:50-02:00
AS
SgPU4KtHBLDY5Hn6QvMJAnyAyYq93msJKM...
2014-10-18T15:19:50-02:00
```
