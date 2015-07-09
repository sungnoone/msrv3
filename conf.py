##Testing host
HOST_IP = "192.168.1.229"
##Official host
#HOST_IP = "192.168.1.230"
HOST_PORT = 8088


DB_IP = "192.168.1.225"
DB_PORT = 27017


# Error code
# 01x000: OK
# 01x001:資料庫查詢失敗
# 01x002:資料庫寫入失敗
# 01x003:資料庫刪除失敗
# 01x004:資料庫更新失敗
# 01x005:
# 01x006:
# 01x007:
# 01x008:
# 01x009:
# 01x010:沒有記錄存在

# 02x002:request fail


# DB -- cn thesaurus
DB_CN = "cn"
COLLECTION_CN_WORDS = "words"
COLLECTION_CN_WORDS_CLASS1 = "words_class1" ## fro demo
COLLECTION_CN_WORDS_BROKEN = "words_broken" ##破音字庫
COLLECTION_CN_WORDS_BROKEN_FONT = "words_broken_font" ##破音關聯詞庫
COLLECTION_CN_WORDS_BROKEN_FONT_LOG = "words_broken_font_log"
COLLECTION_CN_OPTIONS_YEAR = "options_year" ## year options library for demo

#fields name map
#
CN_WORDS_ID = "words_id"
CN_WORDS_CONTENT = "words_content"


#fields name map
#
CN_WORDS_CLASS1_ID = "編號"
CN_WORDS_CLASS1_NAME = "生字"


#broken phonetic library
CN_WORDS_BROKEN_ID = "編號"
CN_WORDS_BROKEN_WORD = "生字"


#broken phonetic with font library
CN_WORDS_BROKEN_FONT_ID = "id"
CN_WORDS_BROKEN_FONT_WORD = "word"
CN_WORDS_BROKEN_FONT_BEFORE_WORD = "before_word"
CN_WORDS_BROKEN_FONT_AFTER_WORD = "after_word"
CN_WORDS_BROKEN_FONT_APPLY_FONT_NAME = "apply_font_name"
CN_ID_PREFIX2 = "CNAA"


#fields name map
#options_year
CN_OPTIONS_YEAR_YEAR = "year"


## msrv system config
DB_MSRV3 = "msrv3" ## application system config db
COLLECTION_MSRV3_USERS = "users" ## msrv3 users account

##fields name mapping
MSRV3_USERS_ID = "id"
MSRV3_USERS_EID = "eid"
MSRV3_USERS_NAME = "name"
MSRV3_USERS_STATE = "state"
MSRV3_USERS_APPS = "apps" ##array
MSRV3_USERS_GROUPS = "groups" ##array
MSRV3_USERS_DESCRIPTION = "description"

