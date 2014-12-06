from flask import jsonify, g
from settings import *

def execute_query(sql, data, conn, cursor):
    try:
        cursor.execute(sql, data)
    except:
        conn.rollback()
        error_info = error_code(Codes.unknown_error, 'execute exception for:' + sql, conn, cursor)
        return error_info
    return None    


def error_code(code, response, conn, cursor):
    close_connection(cursor, conn)
    return jsonify(code = code, response = response)

def success(response):
    return jsonify(code = Codes.ok, response = response)    


def close_connection(cursor, conn):
    cursor.close()
    conn.close()


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

