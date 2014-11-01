#!/usr/bin/python
# -*- coding: utf8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

"""Módulo para comunicación con webservice Factura Electrónica DGI Uruguay
"""

__author__ = "Mariano Reingart <reingart@gmail.com>"
__copyright__ = "Copyright (C) 2014 Mariano Reingart"
__license__ = "GPL 3.0+"
__version__ = "0.5"

# Constantes para configurar el ambiente (testing o productivo):

##WSDL = "https://efactura.dgi.gub.uy:6443/ePrueba/ws_eprueba?wsdl"
LOCATION = "https://efactura.dgi.gub.uy:6443/ePrueba/ws_eprueba"
ACTION = "http://dgi.gub.uyaction/"
        #"http://dgi.gub.uyaction/AWS_EFACTURA.EFACRECEPCIONSOBRE"

import datetime
import xml.dom.minidom
from pysimplesoap.client import SoapClient, SimpleXMLElement
from pysimplesoap.wsse import BinaryTokenSignature
from pysimplesoap import xmlsec


# Por el momento se utilizan llamadas crudas (RAW) y no se parsea el WSDL
##client = SoapClient(wsdl=wsdl, cache="cache")

# Instancio el cliente para consumir el webservice
client = SoapClient(LOCATION, ACTION,
                    namespace="http://dgi.gub.uy", 
                    ns="dgi", 
                    soap_ns="soapenv", trace=True)

# si se usa el WSDL, se puede consultar client.help("EFACRECEPCIONSOBRE")

# Procedimiento tentativo:
# ========================

# leer los datos del comprobante
# NOTA: se podría usar más SimpleXMLElement para armar el xml pythonicamente

cfe = SimpleXMLElement(open("dgicfe_uy.xml").read())
caratula = cfe("DGICFE:Caratula")

# establecer la fecha actual
setattr(caratula, "DGICFE:Fecha", 
                  datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S-03:00"))#utcnow().strftime("%Y-%m-%dT%H:%M:%S"))

# leer el certificado (PEM) del emisor y agregarlo 
cert_lines = open("certificado.crt").readlines()
cert_pem =  ''.join([line for line in cert_lines
                          if not line.startswith("---")])
setattr(caratula, "DGICFE:X509Certificate", cert_pem)

# preparar la plantilla para la info de firma con los namespaces padres (CFE)
plantilla = SimpleXMLElement(xmlsec.SIGN_ENV_TMPL)
plantilla["xmlns:DGICFE"] = plantilla["xmlns:ns0"] = "http://cfe.dgi.gub.uy"
plantilla["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
#plantilla["xsi:schemaLocation"] = "http://cfe.dgi.gub.uy EnvioCFE_v1.11.xsd"

# firmar el CFE, reemplazar valores en la plantilla y agregar la firma al CFE
# NOTA: para verificar la firma usar la plantilla RSA para KeyInfo (comentado)
vars = xmlsec.rsa_sign(cfe.as_xml(), '', "private.key", "password",
                       sign_template=plantilla.as_xml(), c14n_exc=False,
                       cert="".join(cert_lines),
                       key_info_template=xmlsec.KEY_INFO_X509_TMPL,
                       #key_info_template=xmlsec.KEY_INFO_RSA_TMPL,
                      )
firma_xml = (xmlsec.SIGNATURE_TMPL % vars)
cfe("ns0:CFE").import_node(SimpleXMLElement(firma_xml))

# guardo el xml firmado para depuración
open("test.xml", "w").write(cfe.as_xml())
print cfe.as_xml()

# serializar CDATA según el ejemplo
cdata = xml.dom.minidom.CDATASection()
cdata.data = cfe.as_xml()

# construir los parámetros de la llamada al webservice (requerimiento):
param = SimpleXMLElement(
    """<dgi:WS_eFactura.EFACRECEPCIONSOBRE xmlns:dgi="http://dgi.gub.uy"/>""", 
    namespace="http://dgi.gub.uy", prefix="dgi")
data_in = param.add_child("Datain", ns=True)
data_in.add_child("xmlData", cdata, ns=True)

# agregar seguridad WSSE (mensaje firmado digitalmente para autenticacion)
#     usar el certificado unico asociado al RUT emisor emitidos por la 
#     Administración Nacional de Correos (CA: autoridad certificadora actual)

plugin = BinaryTokenSignature(certificate="certificado.crt",
                              private_key="private.key", 
                              password=None,
                              cacert="CorreoUruguayoCA.crt",
                              )
client.plugins += [plugin]

# llamar al método remoto
ret = client.call("AWS_EFACTURA.EFACRECEPCIONSOBRE", param)

# si no hay excepciones, la comunicación ha sido exitosa ("canal seguro"):
#  * DGI acepto la firma digital para el requerimiento (crt)
#  * La respuesta ha sido firmada por un certificado válido (CA)
# TODO: revisar que el certificado de la respuesta sea de DGI (ambiente ok):
#  * RUT 219999830019 en pruebas, RUT 214844360018 en producción

# extraer la respuesta (xml embebido)
res = str(ret.Dataout.xmlData)
print res

# procesar el xml con (por ej. con SimpleXMLElement)
ack = SimpleXMLElement(res)
# analizar elementos de ACKSobre:
caratula = ack("Caratula")
print caratula.RUCReceptor      # 214844360018
print caratula.RUCEmisor        # 160010030018
print caratula.IDRespuesta      # 4214629
print caratula.NomArch
print caratula.FecHRecibido     # 2014-09-16T04:36:33-03:00
print caratula.IDEmisor         # 3009
print caratula.IDReceptor       # 4214629
print caratula.CantidadCFE      # 1
print caratula.Tmst             # 2014-09-16T04:36:35-03:00
for detalle in ack("Detalle"):
    print detalle.Estado        # AS: Sobre Recibido, BS: Sobre Rechazado
    param = detalle.ParamConsulta
    print param.Token           # 1Yw+OMee3hLU8ubi06HekDIVV1FMnCjjiltMMBQfY...
    print param.Fechahora       # 2014-09-16T04:41:35-03:00
