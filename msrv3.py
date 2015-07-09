import sys, os
from flask import Flask, Request, Response, redirect, url_for, jsonify
from flask_cors import *
from pymongo import *
from werkzeug import utils
import json
import bson.json_util
import datetime
import conf
import simplejson
import csv

##custom function class
import dboperate ## mongodb CURD
import vsto ## for vsto service
import uploadsrv ## upload file service
import admin ## web management service
import cn # cn project operation
import security ## user & app security check
import msrv3_index


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


##check user right (disable in production enviroment)
@app.route('/srv/check/')
@cross_origin()
def srv_check():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:connect_srv()"+str(datetime.datetime.now())+"\r\n")
    if (admin.check_user_app("e00278","admin_account_query")):
        log.close()
        return "OK"
    else:
        log.close()
        return "沒有權限！"


## user password check for javascript web client
@app.route('/check/user/password/', methods=["POST"])
@cross_origin()
def check_user_password():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:check_user_password >>>"+str(datetime.datetime.now())+"\r\n")
    #log.write("request result: "+str(request.form)+"\r\n")
    ##Get login info
    try:
        username = request.form["username"]
        password = request.form["password"]
    except Exception as e:
        log.write("request username & password fail! "+str(e)+"\r\n")
        log.close()
        return "1"
    if (username is None) or (username==""):
        log.write("username empty.\r\n")
        log.close()
        return "1"
    queryJSON = {"eid":username,"password":password}
    find_result = dboperate.record_query(conf.DB_MSRV3,conf.COLLECTION_MSRV3_USERS,queryJSON,LOG_DB_OPERATE)
    if(find_result.count()!=1):
        log.write("user not exists.\r\n")
        log.close()
        return "1"
    else:
        log.write("user login: "+str(queryJSON)+"\r\n")
        log.close()
        return "0"
    #return security.check_user_password("","")


##=============================== cn words api =========================================

##=========== for vsto client ==============

## post one record (testing for vsto client)
@app.route('/srv/cn/insert/one/', methods=["POST"])
@cross_origin()
def srv_cn_insert_one():
    return  vsto.srv_cn_insert_one()


# get broken words (for vsto client)
@app.route('/vsto/cn/get/broken/', methods=["GET","POST"])
@cross_origin()
def vsto_cn_get_broken():
    return vsto.vsto_cn_get_broken(conf.DB_CN,conf.COLLECTION_CN_WORDS_BROKEN,LOG_DB_OPERATE)


# get broken words with font (for vsto client)
@app.route('/vsto/cn/get/broken/font', methods=["GET","POST"])
@cross_origin()
def vsto_cn_get_broken_font():
    return vsto.vsto_cn_get_broken(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN_FONT,LOG_DB_OPERATE)


##=========== for web client client ==============


## get all data (response to jqgrid, for web client)
@app.route('/srv/cn/get/all/', methods=["GET","POST"])
@cross_origin()
def srv_cn_get_all():
    return srv_cn_get_all


# get all data (response to DataTables, for web client read only)
@app.route('/srv/cn/get/all/1/', methods=["GET","POST"])
@cross_origin()
def srv_cn_get_all_1():
    ##security
    ##get user id
    user_id = security.get_userid_from_request_1(request)
    ##check user right
    checkResult = security.check_user_app_right(user_id,"/srv/cn/get/all/1/")
    if checkResult == False: ## fail in authentication srv using right
        return_json = {"error":"權限不足"}
        return bson.json_util.dumps(return_json, ensure_ascii=False,indent=2)
    ##run
    return cn.srv_cn_get_all_1()


# get all data (for DataTables read & write)
@app.route('/srv/cn/get/all/2/', methods=["GET","POST"])
@cross_origin()
def srv_cn_get_all_2():
    ##get user id
    user_id = security.get_userid_from_request_2(request)
    ##security
    checkResult = security.check_user_app_right(user_id,"/srv/cn/get/all/2/")
    if checkResult == False: ## fail in authentication srv using right
        #return str([9])
        return_json = {"error":"權限不足"}
        return bson.json_util.dumps(return_json, ensure_ascii=False,indent=2)
    ##run
    return cn.srv_cn_get_all_2(user_id)


# get max id code(for DataTables read)
@app.route('/srv/cn/get/maxid/', methods=["GET","POST"])
@cross_origin()
def srv_cn_get_maxid():
    return cn.srv_cn_get_maxid()


# get all data (response to ajax)
@app.route('/srv/cn/get/type1/', methods=["GET","POST"])
@cross_origin()
def srv_cn_get_type1():
    return cn.srv_cn_get_type1()


## post one record to words_class1, request json (for web client)
@app.route('/srv/cn/insert/single/', methods=["POST"])
@cross_origin()
def srv_cn_insert_single():
    return cn.srv_cn_insert_single()


##jqgrid del record request (for web client)
@app.route('/srv/cn/del/single/', methods=["GET","POST"])
@cross_origin()
def srv_cn_del_single():
    return cn.srv_cn_del_single()


##year option api (for web client)
@app.route('/srv/cn/options/year/', methods=["GET","POST"])
@cross_origin()
def srv_cn_options_year():
    return cn.srv_cn_options_year()


##=============================== cn upload file =========================================

# ##file extension filter
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


#upload file service(no file filter)
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
        if files and uploadsrv.allowed_file(files.filename):
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


#upload csv file
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

        if files and uploadsrv.allowed_csv_file(files.filename):
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


##upload csv file service -- broken phonetic
@app.route('/uploads/csv/broken', methods=['GET', 'POST'])
@cross_origin()
def upload_csv_file_broken():
    return uploadsrv.upload_csv_file_broken()


##upload csv file service -- broken phonetic with font apply
@app.route('/uploads/csv/broken_font', methods=['GET', 'POST'])
@cross_origin()
def upload_csv_file_broken_font():
    return uploadsrv.upload_csv_file_broken_font()


##=========== for msrv3 used ==============


##give index select options , response html code
@app.route('/msrv3/index/menu/', methods=['GET', 'POST'])
@cross_origin()
def msrv3_index_menu():
    ##get user id
    user_id = security.get_userid_from_request_2(request)
    return msrv3_index.msrv3_index_menu(user_id)


##========================================================================


if __name__ == '__main__':
    app.run(host=conf.HOST_IP, port=conf.HOST_PORT)
