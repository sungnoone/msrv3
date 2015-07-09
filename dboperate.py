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


#query record
def record_query(use_db, use_collection, json_content, log_file_path):
    log = open(log_file_path, 'a+')
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
def record_save(use_db, use_collection, json_content, log_file_path):
    log = open(log_file_path, 'a+')
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
def record_update(use_db, use_collection, query_json, update_json, log_file_path):
    log = open(log_file_path, 'a+')
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
def record_delete(use_db, use_collection, query_json, log_file_path):
    log = open(log_file_path, 'a+')
    log.write(">>>...>>>...MODULE:record_update() "+str(datetime.datetime.now())+"\r\n")

    log.write("DB: "+str(use_db)+"\r\n")
    log.write("Collection: "+str(use_collection)+"\r\n")
    log.write("Query Content: "+str(query_json)+"\r\n")

    if not isinstance(query_json, dict):
        log.write("query not JSON object\r\n")
        log.close()
        return False

    try:
        client = MongoClient(conf.DB_IP, conf.DB_PORT)
        db = client[use_db]
        collection = db[use_collection]
        remove_result = collection.remove(query_json)
        log.write("Remove data ok.\r\n")
        client.close()
        log.close()
        return remove_result
    except Exception as e:
        log.write("Remove data error: "+str(e)+"\r\n")
        log.close()
        return False


#query field max value record
def record_query_field_value_max(use_db, use_collection, field_name, log_file_path):
    log = open(log_file_path, 'a+')
    log.write(">>>...>>>...MODULE:record_query_field_value_max() "+str(datetime.datetime.now())+"\r\n")

    log.write("DB: "+str(use_db)+"\r\n")
    log.write("Collection: "+str(use_collection)+"\r\n")
    log.write("Query Content: "+str(field_name)+"\r\n")

    if (field_name is None) or (field_name == ""):
        log.write("field name empty!!\r\n")
        log.close()
        return False

    try:
        client = MongoClient(conf.DB_IP, conf.DB_PORT)
        db = client[use_db]
        collection = db[use_collection]
        find_result = collection.find_one(sort=[(field_name,-1)])
        log.write("query data OK.\r\n")
        client.close()
        log.close()
        return find_result[field_name]
    except Exception as e:
        log.write("query data error: "+str(e)+"\r\n")
        log.close()
        return False
