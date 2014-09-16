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
__version__ = "0.3"

# Constantes para configurar el ambiente (testing o productivo):

##WSDL = "https://efactura.dgi.gub.uy:6443/ePrueba/ws_eprueba?wsdl"
LOCATION = "https://efactura.dgi.gub.uy:6443/ePrueba/ws_eprueba"
ACTION = "http://dgi.gub.uyaction/"
        #"http://dgi.gub.uyaction/AWS_EFACTURA.EFACRECEPCIONSOBRE"

import xml.dom.minidom
from pysimplesoap.client import SoapClient, SimpleXMLElement
from pysimplesoap.wsse import BinaryTokenSignature

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

# leer los datos del comprobante, como CDATA según el ejemplo
cdata = xml.dom.minidom.CDATASection()
cdata.data = "Mariano!" #open("dgicfe_uy.xml").read()

# NOTA: se podria usar SimpleXMLElement para armar el xml pythonicamente

# construir los parámetros de la llamada al webservice (requerimiento):
param = SimpleXMLElement(
    """<dgi:WS_eFactura.EFACRECEPCIONSOBRE xmlns:dgi="http://dgi.gub.uy"/>""", 
    namespace="http://dgi.gub.uy", prefix="dgi")
data_in = param.add_child("Datain", ns=True)
data_in.add_child("xmlData", cdata, ns=True)

# agregar seguridad WSSE (mensaje firmado digitalmente para autenticacion)
#     usar el certificado unico asociado al RUT emisor emitidos por la 
#     Administración Nacional de Correos (CA: autoridad certificadora actual)

plugin = BinaryTokenSignature(certificate="zunimercado.crt",
                              private_key="no_encriptada.key", 
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

# procesar el xml con (por ej. con SimpleXMLElement)
print res