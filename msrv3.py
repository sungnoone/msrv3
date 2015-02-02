import sys, os
from flask import Flask, request, redirect, url_for, jsonify
from flask_cors import *
from pymongo import *
from werkzeug import utils
import json
import bson.json_util
import datetime
import conf
import simplejson
import csv
import chardet


APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_FULL_PATH = APP_PATH+"/msrv3.log"
LOG_SUB_FUNCTION_PATH = APP_PATH+"/function.log"
LOG_DB_OPERATE = APP_PATH+"/db.log"
UPLOAD_FOLDER = APP_PATH+'/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'csv'])
ALLOWED_EXTENSIONS_CSV = set(['csv'])

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#=============================== test service =========================================

## hello world
@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello World!'


@app.route('/srv/')
@cross_origin()
def connect_srv():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:connect_srv()"+str(datetime.datetime.now())+"\r\n")
    return "嘗試連接服務成功！！"


#=============================== cn words api =========================================

# get all data (response to jqgrid)
@app.route('/srv/cn/get/all/', methods=["GET","POST"])
@cross_origin()
def srv_cn_get_all():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_get_all()"+str(datetime.datetime.now())+"\r\n")
    return_json = {"rows":[]}
    return_json["rows"].clear()
    try:
        log.write("query start..."+str(datetime.datetime.now())+"\r\n")
        find_result = record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS_CLASS1, {})
        log.write("query end..."+str(datetime.datetime.now())+"\r\n")
        #s = ""
        log.write("json append start..."+str(datetime.datetime.now())+"\r\n")
        for post in find_result:
            return_json["rows"].append(post)
        log.write("json append end..."+str(datetime.datetime.now())+"\r\n")
        try:
            return_result = bson.json_util.dumps(return_json, ensure_ascii="false")
            log.write("return start..."+str(datetime.datetime.now())+"\r\n")
            log.close()
            return return_result
        except Exception as e:
            log.write("jsonify error: "+str(e)+"\r\n")
            log.close()
            return jsonify({"rows":[]})
    except Exception as e:
        log.write("Query db error! " + str(e) + "\r\n")
        log.close()
        return str("01x001")


# get all data (response to ajax)
@app.route('/srv/cn/get/type1/', methods=["GET","POST"])
@cross_origin()
def srv_cn_get_type1():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_get_type1()"+str(datetime.datetime.now())+"\r\n")
    #return_json = {"items":[]}
    return_json = {"items":[]}
    return_json["items"].clear()
    try:
        log.write("query start..."+str(datetime.datetime.now())+"\r\n")
        find_result = record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS_CLASS1, {})
        log.write("query end..."+str(datetime.datetime.now())+"\r\n")
        #s = ""
        log.write("json append start..."+str(datetime.datetime.now())+"\r\n")
        for post in find_result:
            return_json["items"].append(post)
        log.write("json append end..."+str(datetime.datetime.now())+"\r\n")
        try:
            return_result = bson.json_util.dumps(return_json, ensure_ascii="false")
            log.write("return start..."+str(datetime.datetime.now())+"\r\n")
            log.close()
            return return_result
        except Exception as e:
            log.write("jsonify error: "+str(e)+"\r\n")
            log.close()
            return jsonify({"rows":[]})
    except Exception as e:
        log.write("Query db error! " + str(e) + "\r\n")
        log.close()
        return str("01x001")


# post one record
@app.route('/srv/cn/insert/one/', methods=["POST"])
@cross_origin()
def srv_cn_insert_one():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_insert_one()"+str(datetime.datetime.now())+"\r\n")
    try:
        request_data = request.data.decode("utf-8")
        dataDict = json.loads(request_data)
        log.write("request data content: "+str(request_data)+"\r\n")
        log.write("request data dict: "+str(dataDict)+"\r\n")
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "02x002"

    cn_words_id = ""
    cn_words_content = ""
    try:
        for key, value in dataDict.items():
            if key == conf.CN_WORDS_ID:
                cn_words_id = value
            elif key == conf.CN_WORDS_CONTENT:
                cn_words_content = value
    except Exception as e:
        log.write("parse request json data errot: " + str(e) + "\r\n")
        log.close()
        return str("02x002")

    log.write("before find result\r\n")
    #if exist then update it, if not exist then add
    find_result = record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS, {conf.CN_WORDS_ID:cn_words_id})
    if find_result.count() == 0:
        insert_result = record_save(conf.DB_CN, conf.COLLECTION_CN_WORDS, dataDict)
        if insert_result == False:
            log.write("insert fail: " + str(insert_result) + "\r\n")
            log.close()
            return "01x002"
        else:
            log.write("insert OK: " + str(insert_result) + "\r\n")
            log.close()
            return "01x000"
    else:
        update_json = {conf.CN_WORDS_CONTENT:cn_words_content}
        update_result = record_update(conf.DB_CN, conf.COLLECTION_CN_WORDS, {conf.CN_WORDS_ID:cn_words_id}, update_json)
        if update_result == False:
            log.write("update fail: " + str(update_result) + "\r\n")
            log.close()
            return "01x004"
        else:
            log.write("update OK: " + str(update_result) + "\r\n")
            log.close()
            return "01x000"


#=============================== cn upload file =========================================

#file extension filter
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


#upload file service
@app.route('/uploads/', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE: upload_file()"+str(datetime.datetime.now())+"\r\n")
    if request.method == 'POST':
        log.write("POST"+"\r\n")
        log.write(str(request.files)+"\r\n")
        files = request.files["files[]"]
        log.write(str(files)+"\r\n")
        if files and allowed_file(files.filename):
            filename = utils.secure_filename(files.filename)
            files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            log.close()
            return simplejson.dumps({"files":filename})
            #return redirect(url_for('uploaded_file',filename=filename))
        else:
            log.close()
            return "true"
    else:
        log.write("GET"+"\r\n")
        log.close()
        return "uploads service..."


#file extension filter -- allow csv for import
def allowed_csv_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_CSV


#upload csv file service
@app.route('/uploads/csv/', methods=['GET', 'POST'])
@cross_origin()
def upload_csv_file():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE: upload_csv_file()"+str(datetime.datetime.now())+"\r\n")
    if request.method == 'POST':
        log.write("POST"+"\r\n")
        log.write(str(request.files)+"\r\n")
        files = request.files["files[]"]
        log.write(str(files)+"\r\n")

        if files and allowed_csv_file(files.filename):
            filename = utils.secure_filename(files.filename)
            files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            log.close()
            parse_csv(filename)

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


#parse csv
def parse_csv(filename):
    log = open(LOG_SUB_FUNCTION_PATH, 'a+')
    log.write(">>>...MODULE:parse_csv()"+str(datetime.datetime.now())+"\r\n")
    log.write(filename+"\r\n")
    try:
        #csvfile = csv.reader(open(UPLOAD_FOLDER+"/"+filename,"rt", newline="", encoding="utf-8"), dialect="excel")
        with open(UPLOAD_FOLDER+"/"+filename, 'rt', encoding="utf-8-sig") as csvfile:
            csv_reader = csv.DictReader(csvfile,dialect="excel")
            #jsonfile = open(UPLOAD_FOLDER+"/dumps.json", "w")
            ##every row
            for row in csv_reader:
                json_dump = json.dumps(row, ensure_ascii=False)
                save_result = record_save(conf.DB_CN, conf.COLLECTION_CN_WORDS_CLASS1, eval(json_dump))
                #log.write(row["編號"]+" save into db "+str(save_result)+"\r\n")
        log.close()
    except Exception as e:
        log.write(str(e)+"\r\n")
        log.close()


#=============================== common function =========================================


#query record
def record_query(use_db, use_collection, json_content):
    log = open(LOG_DB_OPERATE, 'a+')
    log.write(">>>...>>>...MODULE:record_query() "+str(datetime.datetime.now())+"\r\n")

    log.write("DB: "+str(use_db)+"\r\n")
    log.write("Collection: "+str(use_collection)+"\r\n")
    log.write("Query Content: "+str(json_content)+"\r\n")

    if not isinstance(json_content, dict):
        log.write("Query content not JSON object\r\n")
        log.close()
        return False

    try:
        client = MongoClient(conf.DB_IP, conf.DB_PORT)
        db = client[use_db]
        collection = db[use_collection]
        find_result = collection.find(json_content)
        log.write("query data OK.\r\n")
        client.close()
        log.close()
        return find_result
    except Exception as e:
        log.write("query data error: "+str(e)+"\r\n")
        log.close()
        return False


#Save record
def record_save(use_db, use_collection, json_content):
    log = open(LOG_DB_OPERATE, 'a+')
    log.write(">>>...>>>...MODULE:record_save() "+str(datetime.datetime.now())+"\r\n")

    log.write("DB: "+str(use_db)+"\r\n")
    log.write("Collection: "+str(use_collection)+"\r\n")
    log.write("Write Content: "+str(json_content)+"\r\n")

    if not isinstance(json_content, dict):
        log.write("Write content not JSON object\r\n")
        log.close()
        return False

    try:
        client = MongoClient(conf.DB_IP, conf.DB_PORT)
        db = client[use_db]
        collection = db[use_collection]
        record_id = collection.insert(json_content)
        log.write("save data OK.\r\n")
        client.close()
        log.close()
        return record_id
    except Exception as e:
        log.write("save data error: "+str(e)+"\r\n")
        log.close()
        return False


#update record(if query not exist, add)
def record_update(use_db, use_collection, query_json, update_json):
    log = open(LOG_DB_OPERATE, 'a+')
    log.write(">>>...>>>...MODULE:record_update() "+str(datetime.datetime.now())+"\r\n")

    log.write("DB: "+str(use_db)+"\r\n")
    log.write("Collection: "+str(use_collection)+"\r\n")
    log.write("Query Content: "+str(query_json)+"\r\n")
    log.write("Update Content: "+str(update_json)+"\r\n")

    if not isinstance(query_json, dict):
        log.write("query not JSON object\r\n")
        log.close()
        return False

    if not isinstance(update_json, dict):
        log.write("update not JSON object\r\n")
        log.close()
        return False

    try:
        client = MongoClient(conf.DB_IP, conf.DB_PORT)
        db = client[use_db]
        collection = db[use_collection]
        update_result = collection.update(query_json, {"$set": update_json}, upsert=True, multi=True)
        log.write("update data OK.\r\n")
        client.close()
        log.close()
        return update_result
    except Exception as e:
        log.write("save data error: "+str(e)+"\r\n")
        log.close()
        return False


#delete record
def record_delete():
    return True


#========================================================================


if __name__ == '__main__':
    app.run(host=conf.HOST_IP, port=conf.HOST_PORT)
