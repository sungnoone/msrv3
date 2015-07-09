import sys, os
from flask import Flask, Request, Response, redirect, url_for, jsonify
from flask_cors import *
import json
import datetime
import conf
import dboperate
import bson.json_util


APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_FULL_PATH = APP_PATH+"/msrv3.log"
LOG_SUB_FUNCTION_PATH = APP_PATH+"/function.log"
LOG_DB_OPERATE = APP_PATH+"/db.log"
UPLOAD_FOLDER = APP_PATH+'/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'csv'])
ALLOWED_EXTENSIONS_CSV = set(['csv'])


## post one record (testing for vsto client)
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


# get broken words (for vsto client)
def vsto_cn_get_broken(db,collection,logfile):
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:vsto_cn_get_broken()"+str(datetime.datetime.now())+"\r\n")
    return_json = {"rows":[]}
    return_json["rows"].clear()
    try:
        #find_result = dboperate.record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN, {}, LOG_DB_OPERATE)
        find_result = dboperate.record_query(db, collection, {}, logfile)
        log.write("db query OK!\r\n")
        for post in find_result:
            return_json["rows"].append(post)
        try:
            return_result = bson.json_util.dumps(return_json, ensure_ascii="false")
            log.write("bson result dump OK!\r\n")
            log.close()
            return return_result
        except Exception as e:
            log.write("bson json util dumps error: "+str(e)+"\r\n")
            log.close()
            return {}
    except Exception as e:
        log.write("Query db error! " + str(e) + "\r\n")
        log.close()
        return str("02x001")
