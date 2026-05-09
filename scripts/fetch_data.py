# -*- coding: utf-8 -*-
"""
Created on Fri May  8 19:43:36 2026

@author: gerva

Generador de tablas: basicos.csv y indicadores.csv 
"""
from pathlib import Path
import pandas as pd
import requests
import datetime as dt

# Ubicación de archivos de salida CSV: dentro de la carpeta /data
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True) 


#---------- BASICOS ----------
# De momento ingreso los datos a mano

cargos = ["Profesor Adjunto",
          "Jefe de Trabajos Prácticos",
          "Ayudante de Primera"]

basicos = [308578.79, 
           265009.91,
           221392.92]

fecha = [dt.date(2026,4,1) for i in range(3)]

basicos = pd.DataFrame(data = {
                    "cargo" : cargos,
                    "basico" : basicos,
                    "fecha" : fecha}
                        )

# Guardo los resultados en /data/basicos.csv
basicos.to_csv(DATA_DIR / "basicos.csv", index=False)


#---------- INDICADORES ----------
# De momento extraigo sólo el último dato de las API correspondientes

url_bcra = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias"
url_datosgob = "https://apis.datos.gob.ar/series/api/series"

# Creo el DataFrame vacío:
indicadores = pd.DataFrame(columns = ["indicador", "valor", "fecha"])


# GARANTIA SALARIAL: extraido de 
# https://unlp.edu.ar/transparencia/transparencia-activa/escalas-salariales/

indicadores.loc[0] = ["Garantía Salarial", 308641.98, dt.date(2025,2,1)]


# DOLAR OFICIAL MINORISTA: extraido de BCRA

dolar_json = requests.get(url_bcra + "/4").json()
dolar_ultimo = dolar_json["results"][0]["detalle"][0]

indicadores.loc[1] = ["Tipo de cambio minorista", dolar_ultimo["valor"], dolar_ultimo["fecha"]]


# CANASTA BASICA TOTAL: extraido de Datos.gob

id_cbt = "?ids=150.1_CSTA_BATAL_0_D_20"
cbt_json = requests.get(url_datosgob + id_cbt + "&start_date=2020-01-01").json()
cbt_ultimo = cbt_json["data"][-1]

indicadores.loc[2] = ["Canasta Básica", cbt_ultimo[-1], cbt_ultimo[-2]]

# Guardo los resultados en /data/indicadores.csv
indicadores.to_csv(DATA_DIR / "indicadores.csv", index=False)
