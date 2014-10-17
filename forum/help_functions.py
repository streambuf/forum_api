from flask import jsonify
from settings import mysql

def execute_query(sql, data, conn, cursor):
    try:
        cursor.execute(sql, data)
        conn.commit()
    except:
        conn.rollback()
        error_info = error_code(4, 'execute exception for:' + sql, conn, cursor)
        return error_info
    return None    


def error_code(code, response, conn, cursor):
    close_connection(conn, cursor)
    return jsonify(code = code, response = response)


def close_connection(conn, cursor):
    cursor.close()
    conn.close()


def get_array(cursor):
    array = []    
    rets = cursor.fetchall()
    for row in rets:
        array.append(row[0])
    return array


def replace_null(param):
    if param is None:
        param = 'false'
    return param    


def is_number(str):
    try:
        int(str)
        return True
    except ValueError:
        return False
