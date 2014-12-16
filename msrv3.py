import sys, os
from flask import Flask
from flask_cors import *
from pymongo import *
import json
import bson.json_util
import datetime

import conf


app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_FULL_PATH = APP_PATH+"/msrv3.log"
LOG_SUB_FUNCTION_PATH = APP_PATH+"/function.log"
LOG_DB_OPERATE = APP_PATH+"/db.log"

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

# get all data
@app.route('/srv/cn/get/all/', methods=["GET"])
@cross_origin()
def srv_cn_get_all():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_get_all()"+str(datetime.datetime.now())+"\r\n")
    try:
        #Query all data
        find_result = record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS, {})
        s = ""
        for post in find_result:
            s += str(post) + "</br>"
        log.close()
        return str(s)
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
