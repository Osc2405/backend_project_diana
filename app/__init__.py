
from flask import Flask,jsonify, request
from logging import exception
from flask_sqlalchemy import SQLAlchemy
from sqlite3.dbapi2 import Cursor
import os
import sqlite3
from sqlite3 import Error

from h11 import Data
from .models.models import db,consultas
import ast
import json

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
ruta_db=Config.DATABASE_PATH
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(Config.DATABASE_PATH)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


###############################


from selenium import webdriver
from datetime import date,timedelta
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options
options = Options()
options.headless = True

today = date.today()
d1 = today.strftime("%d/%m/%Y")
competencias=['50M Libre/50M Free', '100M Libre/100M Free', '200M Libre/200M Free', '400M Libre/400M Free', '800M Libre/800M Free', '1500M Libre/1500M Free', '50M Espalda/50M Back', '100M Espalda/100M Back', '200M Espalda/200M Back', '50M Pecho/50M Breast', '100M Pecho/100M Breast', '200M Pecho/200M Breast', '50M Mariposa/50M Fly', '100M Mariposa/100M Fly', '200M Mariposa/200M Fly', '200M Comb.ind/200M Medley', '400M Comb.ind/400M Medley']


def ConsultarRanking():
    lista=[]
    URL="https://www.colombiaacuatica.com/backtun/torneos/fecna/sw/rankingfecna01.php"
    driver = webdriver.Chrome(options=options)
    for event in competencias:
        URL="https://www.colombiaacuatica.com/backtun/torneos/fecna/sw/rankingfecna01.php"
        driver.get(URL)
        current_url=driver.current_url
        

        startDate= driver.find_element(By.XPATH, value="/html/body/form/div[1]/div[1]/input")
        endDate = driver.find_element(By.XPATH, value="/html/body/form/div[1]/div[2]/input")

        ##Envio de fecha inicial y final
        startYear=today-timedelta(365)
        startYear = startYear.strftime("%d/%m/%Y")
        startYear=startYear[6:]


        startDate.send_keys("01/01/{}".format(startYear))
        endDate.send_keys(d1)

        ##Dropdown menus
        driver.find_element(By.XPATH,value="//select[@name='nLiga']/option[text()='VALLE']").click()
        driver.find_element(By.XPATH,value="//select[@name='nPrueba']/option[text()='{}']".format(event)).click()
        
        ##Place
        place= driver.find_element(By.XPATH, value="/html/body/form/div[1]/div[4]/input")
        place.clear()
        place.send_keys("10")

        
        ##Send form
        driver.find_element(By.XPATH,value="/html/body/form/div[3]/div[2]/button").click()

        wait(driver, 5).until(EC.url_changes(current_url))
        a = driver.find_elements(By.CLASS_NAME,value="row")
        lista_original=[]
        for i in a:
            l1=i.text.split("\n")
            l1.append(event)
            lista_original.append(l1)

        if event==competencias[0]:
            lista.extend(lista_original[3:-1])
        else:
            lista.extend(lista_original[4:-1])
    driver.close()
    lista[0][-1]="Competencia"
    return lista

######################


##RUTAS##
@app.route("/")
def index():
    return "Hola"

@app.route("/api/ranking",methods=["GET"])
def getRanking():
    try:
        ranking= consultas.query.order_by(consultas.id.desc()).first()
        to_return=consultas.serialize(ranking)
        to_return["data"]=ast.literal_eval(to_return["data"])
        return jsonify(to_return),200

    except Exception:
        exception("[SERVER]: Error ->")
        return jsonify({"message": "Ha ocurrido un error"}),500

@app.route("/api/update",methods=["GET"])
def updateRanking():
    try:
        body_data=json.loads(request.data)
        if "pass" not in body_data:
            return jsonify({"message": "No se ha proporcionado una contraseña"})
        if body_data["pass"] != Config.DB_PASSWORD:
            return jsonify({"message": "Contraseña incorrecta"})
        ranking= consultas.query.filter_by(date=str(d1)).first()
        if ranking:
            return jsonify({"message": "El ranking está actualizado a la fecha"}),200
        
        lista=ConsultarRanking()
        lista_str="{}".format(lista)
        nueva_cosulta=consultas(date=d1,data=lista_str)
        db.session.add(nueva_cosulta)
        db.session.commit()
        return jsonify({"message":"Success"}),200

    except Exception:
        exception("[SERVER]: Error ->")
        return jsonify({"message": "Ha ocurrido un error"}),500


