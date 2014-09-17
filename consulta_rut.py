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

"""Módulo para Consulta RUT con webservice Factura Electrónica DGI Uruguay
"""

__author__ = "Mariano Reingart <reingart@gmail.com>"
__copyright__ = "Copyright (C) 2014 Mariano Reingart"
__license__ = "GPL 3.0+"
__version__ = "0.5"

# Constantes para configurar el ambiente (testing o productivo):

##WSDL = "https://efactura.dgi.gub.uy:6470/ePrueba/ws_personaGetActEmpresarialPrueba?wsdl"
LOCATION = "https://efactura.dgi.gub.uy:6470/ePrueba/ws_personaGetActEmpresarialPrueba"
ACTION = "DGI_Modernizacion_Consolidadoaction/"
        #"http://dgi.gub.uyaction/AWS_EFACTURA.EFACRECEPCIONSOBRE"

import datetime
import xml.dom.minidom
from pysimplesoap.client import SoapClient, SimpleXMLElement
from pysimplesoap.wsse import BinaryTokenSignature
from pysimplesoap import xmlsec

# El namespace relativo "DGI_Modernizacion_Consolidado" hace fallar a libxml2
# con la siguiente excepción por estar deprecado en el estándar XML c14n:
#   lxml.etree.C14NError: Relative namespace UR is invalid here : (null)
xmlsec.lxml = None                  # deshabilitar lxml y usar c14n.py

# Por el momento se utilizan llamadas crudas (RAW) y no se parsea el WSDL
##client = SoapClient(wsdl=wsdl, cache="cache")

# Instancio el cliente para consumir el webservice
client = SoapClient(LOCATION, ACTION,
                    namespace="DGI_Modernizacion_Consolidado", 
                    ns="dgi", 
                    soap_ns="soapenv", trace=True)

# si se usa el WSDL, se puede consultar client.help("EFACRECEPCIONSOBRE")

# construir los parámetros de la llamada al webservice (requerimiento):
param = SimpleXMLElement(
    """<dgi:WS_PersonaGetActEmpresarial.Execute xmlns:dgi="DGI_Modernizacion_Consolidado" />""", 
    namespace="DGI_Modernizacion_Consolidado", prefix="dgi")
rut = param.add_child("Rut", "21047573001133", ns=True)

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
ret = client.call("AWS_PERSONAGETACTEMPRESARIAL.Execute", param)

# si no hay excepciones, la comunicación ha sido exitosa ("canal seguro"):
#  * DGI acepto la firma digital para el requerimiento (crt)
#  * La respuesta ha sido firmada por un certificado válido (CA)
# TODO: revisar que el certificado de la respuesta sea de DGI (ambiente ok):
#  * RUT 219999830019 en pruebas, RUT 214844360018 en producción

# extraer la respuesta (xml encapsulado)
res = str(ret.Data)
print res

# procesar el xml con (por ej. con SimpleXMLElement)
ret = SimpleXMLElement(res)
# analizar elementos de ACKSobre:
print ret.RUT
print ret.Denominacion
print ret.NombreFantasia
print ret.TipoEntidad
print ret.DescripcionTipoEntidad
print ret.EstadoActividad
print ret.FechaInicioActividad
for item in ret.WS_DomFiscalLocPrincipal:
    print item.Calle_Nom, item.Calle_id, item.Dom_Pta_Nro
    print item.Loc_Nom
