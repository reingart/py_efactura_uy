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
