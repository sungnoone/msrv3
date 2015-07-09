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

import dboperate

APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_ADMIN_PATH = APP_PATH+"/msrv3_admin.log"


##================================================================================================





##================================================================================================

##/admin/account/add
def admin_account_add():
    pass


##/admin/account/query
def admin_account_query_all():
    pass


## Query user by eid
def admin_account_query_one(eid):
   return ""


##/admin/account/query
def admin_account_edit():
    pass












##================================================================================================




