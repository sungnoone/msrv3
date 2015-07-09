import sys, os
from flask import Flask, Request, Response, redirect, url_for, jsonify
from flask_cors import *
import json
import bson.json_util
import datetime
import conf
import simplejson
import csv


import conf
import dboperate


APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_FULL_PATH = APP_PATH+"/cn.log"
LOG_SUB_FUNCTION_PATH = APP_PATH+"/function.log"
LOG_DB_OPERATE = APP_PATH+"/db.log"


##=========== for DataTables ==============


##for DataTables
##query only
def srv_cn_get_all_1():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_get_all_1()"+str(datetime.datetime.now())+"\r\n")
    return_json = {"rows":[]}
    return_json["rows"].clear()
    try:
        #log.write("query start..."+str(datetime.datetime.now())+"\r\n")
        #log.write(LOG_DB_OPERATE+"\r\n")
        find_result = dboperate.record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN_FONT, {}, LOG_DB_OPERATE)
        #log.write("query end..."+str(datetime.datetime.now())+"\r\n")
        #log.write("json append start..."+str(datetime.datetime.now())+"\r\n")
        for post in find_result:
            return_json["rows"].append(post)
        #log.write("json append end..."+str(datetime.datetime.now())+"\r\n")

        try:
            return_result = bson.json_util.dumps(return_json, ensure_ascii=False,indent=2)
            #log.write("return start..."+str(datetime.datetime.now())+"\r\n")
            #log.write("return_result..."+str(return_result)+"\r\n")
            log.close()
            return return_result
        except Exception as e:
            log.write("jsonify error: "+str(e)+"\r\n")
            log.close()
            return jsonify({"rows":[]})
    except Exception as e:
        log.write("error: " + str(e) + "\r\n")
        log.close()
        return jsonify({"rows":[]})

## for DataTables
## for read and write
def srv_cn_get_all_2(user_id):
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_get_all_2() "+str(datetime.datetime.now())+"\r\n")
    try:
        request_data = request.data.decode("utf-8")
        log.write("request: "+str(request)+"\r\n")
        log.write("request form: "+str(request.form)+"\r\n")
        log.write("request data: "+str(request_data)+"\r\n")
        ## request send action、id[]
        dataAction = str(request.form.getlist("action")[0])
        log.write("request data operation method: "+str(dataAction)+"\r\n")
        if dataAction == "create":
            ## Create
            ##get max id
            find_result = dboperate.record_query_field_value_max(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN_FONT, "id", LOG_DB_OPERATE)
            data_1 = conf.CN_ID_PREFIX2+str(int(find_result[4:])+1).zfill(8)
            data_2 = request.form.getlist("data["+conf.CN_WORDS_BROKEN_FONT_BEFORE_WORD+"]")[0]
            data_3 = request.form.getlist("data["+conf.CN_WORDS_BROKEN_FONT_WORD+"]")[0]
            data_4 = request.form.getlist("data["+conf.CN_WORDS_BROKEN_FONT_AFTER_WORD+"]")[0]
            data_5 = request.form.getlist("data["+conf.CN_WORDS_BROKEN_FONT_APPLY_FONT_NAME+"]")[0]
            ##insert json
            newJSON = {
                conf.CN_WORDS_BROKEN_FONT_ID:data_1,
                conf.CN_WORDS_BROKEN_FONT_BEFORE_WORD:data_2,
                conf.CN_WORDS_BROKEN_FONT_WORD:data_3,
                conf.CN_WORDS_BROKEN_FONT_AFTER_WORD:data_4,
                conf.CN_WORDS_BROKEN_FONT_APPLY_FONT_NAME:data_5
            }
            log.write("newJSON: "+str(newJSON)+"\r\n")
            ##Insert data
            find_result = dboperate.record_save(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN_FONT, newJSON, LOG_DB_OPERATE)
            if find_result != False:
                cn_action_log(user_id,dataAction,newJSON) ##write log db
        elif dataAction == "edit":
            ## Edit
            data_1 = request.form.getlist("data["+conf.CN_WORDS_BROKEN_FONT_ID+"]")[0]
            data_2 = request.form.getlist("data["+conf.CN_WORDS_BROKEN_FONT_BEFORE_WORD+"]")[0]
            data_3 = request.form.getlist("data["+conf.CN_WORDS_BROKEN_FONT_WORD+"]")[0]
            data_4 = request.form.getlist("data["+conf.CN_WORDS_BROKEN_FONT_AFTER_WORD+"]")[0]
            data_5 = request.form.getlist("data["+conf.CN_WORDS_BROKEN_FONT_APPLY_FONT_NAME+"]")[0]
            queryJSON = {
                conf.CN_WORDS_BROKEN_FONT_ID:data_1
            }
            updateJSON={
                conf.CN_WORDS_BROKEN_FONT_BEFORE_WORD:data_2,
                conf.CN_WORDS_BROKEN_FONT_WORD:data_3,
                conf.CN_WORDS_BROKEN_FONT_AFTER_WORD:data_4,
                conf.CN_WORDS_BROKEN_FONT_APPLY_FONT_NAME:data_5
            }
            log.write("queryJSON: "+str(queryJSON)+"\r\n")
            log.write("updateJSON: "+str(updateJSON)+"\r\n")
            ##update data
            find_result = dboperate.record_update(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN_FONT, queryJSON, updateJSON, LOG_DB_OPERATE)
            if find_result != False:
                cn_action_log(user_id,dataAction,updateJSON) ##write log db
        elif dataAction == "remove":
            dataId = request.form.getlist("id[]")[0]
            ## Delete
            queryJSON = {
                conf.CN_WORDS_BROKEN_FONT_ID:dataId
            }
            log.write("delete queryJSON: "+str(queryJSON)+"\r\n")
            ##query record for log
            query_result = dboperate.record_query(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN_FONT,queryJSON,LOG_DB_OPERATE)
            s = []
            for post in query_result:
                s.append(post)
            ##main function action
            find_result = dboperate.record_delete(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN_FONT, queryJSON, LOG_DB_OPERATE)
            if find_result != False:
                cn_action_log(user_id,dataAction,s) ##write log db
        else:
            ## Other
            log.write("dataAction: "+str(dataAction)+"\r\n")
            log.close()
            return str([0])
        #return "01x000"
        if find_result==False:
            log.close()
            return str([0])
        else:
            log.close()
            return str([-1])
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        #return "02x002"
        return str([0])

##for DataTables
##get max id
def srv_cn_get_maxid():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:srv_cn_get_maxid() "+str(datetime.datetime.now())+"\r\n")
    ##get max id
    find_result = dboperate.record_query_field_value_max(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN_FONT, "id", LOG_DB_OPERATE)
    maxid = conf.CN_ID_PREFIX2+str(int(find_result[4:])+1).zfill(8)
    log.write("maxid: "+maxid+"\r\n")
    log.close()
    return str(maxid)


## =========== for jqgrid test ============== ##


##get all data (response to jqgrid, for web client)
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


##get all data (response to ajax)
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

##======================================================================================##


##log record
def cn_action_log(user_id,actionStr,logStr):
    create_log = {"user":user_id,"action":actionStr,"content":logStr,"timestamp":str(datetime.datetime.now())}
    find_result = dboperate.record_save(conf.DB_CN, conf.COLLECTION_CN_WORDS_BROKEN_FONT_LOG, create_log, LOG_DB_OPERATE)
    if find_result==False:
        log = open(LOG_FILE_FULL_PATH, 'a+')
        log.write(">>>...MODULE:cn_action_log: "+str(datetime.datetime.now())+"\r\n")
        log.write("Saving log fail: "+str(find_result)+"\r\n")
        log.close()
        return False
    else:
        return True

