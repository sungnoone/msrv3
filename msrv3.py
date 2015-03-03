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
import dboperate


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


##=============================== cn words api =========================================

##=========== for vsto client ==============


## post one record (testing for vsto client)
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
    find_result = dboperate.record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS, {conf.CN_WORDS_ID:cn_words_id}, LOG_DB_OPERATE)
    if find_result.count() == 0:
        insert_result = dboperate.record_save(conf.DB_CN, conf.COLLECTION_CN_WORDS, dataDict, LOG_DB_OPERATE)
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
        update_result = dboperate.record_update(conf.DB_CN, conf.COLLECTION_CN_WORDS, {conf.CN_WORDS_ID:cn_words_id}, update_json, LOG_DB_OPERATE)
        if update_result == False:
            log.write("update fail: " + str(update_result) + "\r\n")
            log.close()
            return "01x004"
        else:
            log.write("update OK: " + str(update_result) + "\r\n")
            log.close()
            return "02x000"


##=========== for web client client ==============

# get all data (response to jqgrid, for web client)
@app.route('/srv/cn/get/all/', methods=["GET","POST"])
@cross_origin()
def srv_cn_get_all():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_get_all()"+str(datetime.datetime.now())+"\r\n")
    return_json = {"rows":[]}
    return_json["rows"].clear()
    try:
        log.write("query start..."+str(datetime.datetime.now())+"\r\n")
        log.write(LOG_DB_OPERATE+"\r\n")
        find_result = dboperate.record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS_CLASS1, {}, LOG_DB_OPERATE)
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
        return str("02x001")


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
        find_result = dboperate.record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS_CLASS1, {}, LOG_DB_OPERATE)
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
        return str("02x001")


## post one record to words_class1, request json (for web client)
@app.route('/srv/cn/insert/single/', methods=["POST"])
@cross_origin()
def srv_cn_insert_single():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_insert_single()"+str(datetime.datetime.now())+"\r\n")
    try:
        request_data = request.data.decode("utf-8")
        #log.write(str(request_data)+"\r\n")
        dataDict = json.loads(request_data)
        log.write("request data content: "+str(request_data)+"\r\n")
        log.write("request data dict: "+str(dataDict)+"\r\n")
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "02x002"

    cn_words_class1_id = ""
    try:
        for key, value in dataDict.items():
            log.write(key + "\r\n")
            if key == conf.CN_WORDS_CLASS1_ID:
                cn_words_class1_id = value
            #elif key == conf.CN_WORDS_CLASS1_NAME:
            #    cn_words_class1_content = value

    except Exception as e:
        log.write("parse request json data error: " + str(e) + "\r\n")
        log.close()
        return "01x000"

    log.write("before find result\r\n")
    #if exist then update it, if not exist then add
    find_result = dboperate.record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS_CLASS1, {conf.CN_WORDS_CLASS1_ID:cn_words_class1_id}, LOG_DB_OPERATE)
    if find_result.count() == 0:
        #return "insert"
        insert_result = dboperate.record_save(conf.DB_CN, conf.COLLECTION_CN_WORDS_CLASS1, dataDict, LOG_DB_OPERATE)
        if insert_result == False:
            log.write("insert fail: " + str(insert_result) + "\r\n")
            log.close()
            return "01x002"
        else:
            log.write("insert OK: " + str(insert_result) + "\r\n")
            log.close()
            return "01x000"
    else:
        #return "update"
        update_result = dboperate.record_update(conf.DB_CN, conf.COLLECTION_CN_WORDS_CLASS1, {conf.CN_WORDS_CLASS1_ID:cn_words_class1_id}, dataDict, LOG_DB_OPERATE)
        if update_result == False:
            log.write("update fail: " + str(update_result) + "\r\n")
            log.close()
            return "01x004"
        else:
            log.write("update OK: " + str(update_result) + "\r\n")
            log.close()
            return "01x000"


##jqgrid del record request (for web client)
@app.route('/srv/cn/del/single/', methods=["GET","POST"])
@cross_origin()
def srv_cn_del_single():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_del_single()"+str(datetime.datetime.now())+"\r\n")
    try:
        request_data = request.data.decode("utf-8")
        log.write(str(request_data)+"\r\n")
        #dataDict = json.loads(request_data)
        log.write("request data content: "+str(request_data)+"\r\n")
        #log.write("request data dict: "+str(dataDict)+"\r\n")
        return "01x000"

        log.close()
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "02x002"


##year option api (for web client)
@app.route('/srv/cn/options/year/', methods=["GET","POST"])
@cross_origin()
def srv_cn_options_year():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_options_year()"+str(datetime.datetime.now())+"\r\n")
    return_json = []
    return_json.clear()
    find_result = dboperate.record_query(conf.DB_CN, conf.COLLECTION_CN_OPTIONS_YEAR, {}, LOG_DB_OPERATE)
    for post in find_result:
        return_json.append(post)
    try:
        return_result = bson.json_util.dumps(return_json, ensure_ascii="false")
        log.close()
        return return_result
    except Exception as e:
        log.write("jsonify error: "+str(e)+"\r\n")
        log.close()
        return return_result


##=============================== cn upload file =========================================

##file extension filter
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
@app.route('/uploads/csv', methods=['GET', 'POST'])
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


#parse csv records into db
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
                save_result = dboperate.record_save(conf.DB_CN, conf.COLLECTION_CN_WORDS_CLASS1, eval(json_dump), LOG_DB_OPERATE)
                #log.write(row["編號"]+" save into db "+str(save_result)+"\r\n")
        log.close()
    except Exception as e:
        log.write(str(e)+"\r\n")
        log.close()


#upload broken phonetic csv file service
@app.route('/uploads/csv/broken', methods=['GET', 'POST'])
@cross_origin()
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
            parse_csv_broken(filename)

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


#parse csv records into db -- broken phonetic
def parse_csv_broken(filename):
    log = open(LOG_SUB_FUNCTION_PATH, 'a+')
    log.write(">>>...MODULE:parse_csv_broken()"+str(datetime.datetime.now())+"\r\n")
    log.write(filename+"\r\n")
    try:
        with open(UPLOAD_FOLDER+"/"+filename, 'rt', encoding="utf-8-sig") as csvfile:
            csv_reader = csv.DictReader(csvfile,dialect="excel")
            for row in csv_reader:
                json_dump = json.dumps(row, ensure_ascii=False)
                save_result = dboperate.record_save(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN, eval(json_dump), LOG_DB_OPERATE)
        log.close()
    except Exception as e:
        log.write(str(e)+"\r\n")
        log.close()


#=============================== dynamic columns =========================================


#upload csv file service
@app.route('/grid/col/names', methods=['GET'])
@cross_origin()
def grid_col_names():
    col_names = ['Edit Actions','編號','年度','年級','課次','生字','生字注音','部首','部首注音','總筆畫','部首外筆畫','字義教學','造詞教學-造詞','造詞教學1','造詞教學2','成語教學','字形辨別','字音辨別','教學圖卡']
    col_model = [{ 'name':"編號", 'index':'編號', 'sorttype':"int", 'width':20,'editable':'true','editoptions':'{readonly:"readonly"}'}]

    return jsonify(col_names=col_names, col_model=col_model)


#========================================================================


if __name__ == '__main__':
    app.run(host=conf.HOST_IP, port=conf.HOST_PORT)
