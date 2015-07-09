import sys, os
import datetime
import bson.json_util

import conf
import dboperate

APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_SECURITY_PATH = APP_PATH+"/msrv3_security.log"


##================================================================================================


## get user id from request method 1, for DataTables GET request
def get_userid_from_request_1(request):
    log = open(LOG_FILE_SECURITY_PATH, 'a+')
    log.write(">>>...MODULE:get_userid_from_request_1 >>>"+str(datetime.datetime.now())+"\r\n")
    ## check if client send request data including user id??
    try:
        log.write("request: "+str(request)+"\r\n")
        user_id = request.args["user_id"]
        if(user_id is None) or (user_id==""): ##no user_id
            log.write("No user id!\r\n")
            log.close()
            return ""
        log.close()
        return user_id
    except Exception as e:
        log.write("request user_id error: "+str(e)+"\r\n")
        log.close()
        return ""


## get user id from request method 2, for DataTables Editor POST request
def get_userid_from_request_2(request):
    log = open(LOG_FILE_SECURITY_PATH, 'a+')
    log.write(">>>...MODULE:get_userid_from_request_2 >>>"+str(datetime.datetime.now())+"\r\n")
    ## check if client send request data including user id??
    try:
        log.write("request form: "+str(request.form)+"\r\n")
        user_id = str(request.form.getlist("user_id")[0])
        log.write("get user id: "+str(user_id)+"\r\n")
        if(user_id is None) or (user_id==""): ##no user_id
            log.write("No user id!\r\n")
            log.close()
            return ""
        log.close()
        return user_id
    except Exception as e:
        log.write("request user_id error: "+str(e)+"\r\n")
        log.close()
        return ""


##================================================================================================


##check user right
def check_user_app_right(user_id,srvName):
    log = open(LOG_FILE_SECURITY_PATH, 'a+')
    log.write(">>>...MODULE:check_user_app_right()"+str(datetime.datetime.now())+"\r\n")
    if(user_id is None) or (user_id==""): ##no user_id
        log.write("No user id!\r\n")
        log.close()
        return False

    log.write("request user_id: "+str(user_id)+"\r\n")
    ##match user & state=0 & app_name in apps
    queryStr = {conf.MSRV3_USERS_EID:user_id, "state":0,"srvs":{"$elemMatch":{"srv":srvName}}}
    find_result = dboperate.record_query(conf.DB_MSRV3, conf.COLLECTION_MSRV3_USERS, queryStr, LOG_FILE_SECURITY_PATH)
    if (find_result is None) or (find_result.count()!=1):
        log.write("沒有帳號或帳號重複存在或無權限！！\r\n")
        log.close()
        return False
    else:
        user = find_result[0]
        log.write("user json: "+str(user)+"\r\n")
        log.close()
        return True


##check user name and password
def check_user_password(user_id,user_password):
    log = open(LOG_FILE_SECURITY_PATH, 'a+')
    log.write(">>>...MODULE:check_user_password()"+str(datetime.datetime.now())+"\r\n")
    if(user_id is None) or (user_id==""): ##no user_id
        log.write("No user id!\r\n")
        log.close()
        return False
    queryJSON = {"eid":user_id,"password":user_password}
    find_result = dboperate.record_query(conf.DB_MSRV3, conf.COLLECTION_MSRV3_USERS,queryJSON,LOG_FILE_SECURITY_PATH)
    if find_result.count()!=1:
        log.write("check user password fail: "+str(find_result.count())+"\r\n")
        return False
    log.close()
    return True