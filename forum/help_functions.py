from flask import jsonify, g
from settings import *

def execute_query(sql, data, cursor):
    try:
        cursor.execute(sql, data)
        conn.commit()
    except:
        conn.rollback()
        error_info = error_code(Codes.unknown_error, 'execute exception for:' + sql, cursor)
        return error_info
    return None    


def error_code(code, response, cursor):
    close_connection(cursor)
    return jsonify(code = code, response = response)

def success(response):
    return jsonify(code = Codes.ok, response = response)    


def close_connection(cursor):
    cursor.close()


def get_array(cursor):
    array = []    
    rets = cursor.fetchall()
    for row in rets:
        array.append(row[0])
    return array

def build_dict_params(request, array):
    dict = {}
    for a in array:
        dict[a] = request.args.get(a)
    return dict    

def is_number(str):
    try:
        int(str)
        return True
    except ValueError:
        return False


cursor = conn.cursor()

sql = ("SELECT MAX(id) FROM user")
cursor.execute(sql)
conn.commit()
ret = cursor.fetchone()
# create id for user        
if ret[0] is None:
    g.cur_user_id = 1
else:
    g.cur_user_id = ret[0] + 1