import sys, os
from flask import Flask, Request, Response, redirect, url_for, jsonify, request
from pymongo import *
from werkzeug import utils
import json
import bson.json_util
import datetime
import conf
import simplejson
import csv
import dboperate


APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_FULL_PATH = APP_PATH+"/msrv3.log"
LOG_SUB_FUNCTION_PATH = APP_PATH+"/function.log"
LOG_DB_OPERATE = APP_PATH+"/db.log"
UPLOAD_FOLDER = APP_PATH+'/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'csv'])
ALLOWED_EXTENSIONS_CSV = set(['csv'])


app = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


##===========================================================================##


##upload csv file service -- broken phonetic
def upload_csv_file_broken():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE: upload_csv_file_broken()"+str(datetime.datetime.now())+"\r\n")
    if request.method == 'POST':
        log.write("POST"+"\r\n")
        log.write(str(request.files)+"\r\n")
        files = request.files["files[]"]
        log.write(str(files)+"\r\n")

        if files and allowed_csv_file(files.filename):
            filename = utils.secure_filename(files.filename)
            files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            log.close()
            ##parse broken csv file content, import into db
            parse_csv_broken(filename,conf.DB_CN,conf.COLLECTION_CN_WORDS_BROKEN)
            ##for testing only
            #parse_csv_broken(filename,conf.DB_CN,"words_test")

            return simplejson.dumps({"files":[
                {"name":filename,"error":"00x000"}
            ]})
        else:
            log.close()
            return simplejson.dumps({"files":[
                {"name":"error","error":"00x001"}
            ]})
            #return simplejson.dumps({"status":"00x001"})
    else:
        log.write("GET"+"\r\n")
        log.close()
        return "uploads csv service..."


##upload csv file service -- broken phonetic with font apply
def upload_csv_file_broken_font():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE: upload_csv_file_broken_font()"+str(datetime.datetime.now())+"\r\n")
    if request.method == 'POST':
        log.write("POST"+"\r\n")
        log.write(str(request.files)+"\r\n")
        files = request.files["files[]"]
        log.write(str(files)+"\r\n")

        if files and allowed_csv_file(files.filename):
            filename = utils.secure_filename(files.filename)
            files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            log.close()
            ##parse broken csv file content, import into db
            parse_csv_broken(filename,conf.DB_CN,conf.COLLECTION_CN_WORDS_BROKEN_FONT)
            ##for testing only
            #parse_csv_broken(filename,conf.DB_CN,"words_test")

            return simplejson.dumps({"files":[
                {"name":filename,"error":"00x000"}
            ]})
        else:
            log.close()
            return simplejson.dumps({"files":[
                {"name":"error","error":"00x001"}
            ]})
            #return simplejson.dumps({"status":"00x001"})
    else:
        log.write("GET"+"\r\n")
        log.close()
        return "uploads csv service..."
    return "broken with font"


##===========================================================================##


#parse csv records into db -- broken phonetic
def parse_csv_broken(filename,dest_db,dest_collection):
    log = open(LOG_SUB_FUNCTION_PATH, 'a+')
    log.write(">>>...MODULE:parse_csv_broken()"+str(datetime.datetime.now())+"\r\n")
    log.write(filename+"\r\n")
    try:
        with open(UPLOAD_FOLDER+"/"+filename, 'rt', encoding="utf-8-sig") as csvfile:
            csv_reader = csv.DictReader(csvfile,dialect="excel")
            for row in csv_reader:
                json_dump = json.dumps(row, ensure_ascii=False)
                save_result = dboperate.record_save(dest_db,dest_collection, eval(json_dump), LOG_DB_OPERATE)
        log.close()
    except Exception as e:
        log.write(str(e)+"\r\n")
        log.close()


##file extension filter
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


#file extension filter -- allow csv for import
def allowed_csv_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_CSV