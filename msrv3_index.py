import sys, os
from flask import Flask, Request, Response, redirect, url_for, jsonify
from flask_cors import *
from pymongo import *
from werkzeug import utils
import datetime
import html
import conf
import dboperate


APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_MSRV3_INDEX = APP_PATH+"/msrv3_index.log"


##=========== for msrv3 used ==============


## index menu html
def msrv3_index_menu(user_id):
    log = open(LOG_FILE_MSRV3_INDEX, 'a+')
    log.write(">>>...MODULE:msrv3_index_menu() "+str(datetime.datetime.now())+"\r\n")
    log.write(user_id+"\r\n")
    #s = '<div data-role="collapsible" data-collapsed="false" data-theme="b" data-content-theme="d"><h3>詞庫維護</h3><ul data-role="listview" data-theme="c"><li><a rel="external" href="1broken_edit.html">多音字體對應表維護</a></li><li><a rel="external" href="1broken_import.html">匯入多音字資料</a></li><li><a rel="external" href="1brokfont_im.html">匯入多音字(套字體)資料</a></li></ul></div><div data-role="collapsible" data-collapsed="false" data-theme="b" data-content-theme="d"><h3>功能實驗</h3></div>'
    #ens = html.escape(s,quote=True)
    if(user_id is None) or (user_id==""):
        log.close()
        return False
    find_result = dboperate.record_query(conf.DB_MSRV3,conf.COLLECTION_MSRV3_USERS,{"eid":user_id},LOG_FILE_MSRV3_INDEX)
    index_html = find_result[0]["html"][0]["index"]
    un_index_html = html.unescape(index_html)
    log.write(str(un_index_html)+"\r\n")
    log.close()
    return un_index_html