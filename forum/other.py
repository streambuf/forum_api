from flask import Blueprint, jsonify, request, Flask, g
from settings import *
from help_functions import *

other = Blueprint('other', __name__, url_prefix='/db/api')

@other.route('/clear/', methods=['POST'])
def clear():
    conn = conn_pool.get_connection()
    cursor = conn.cursor()    
    
    tables = ['followers', 'subscriptions', 'post', 'thread', 'forum', 'user']

    sql = ("SET FOREIGN_KEY_CHECKS = 0;")
    is_error = execute_query(sql, None, conn, cursor)
    if is_error:
        return is_error

    for table in tables:
        sql = ("TRUNCATE TABLE " + table)
        is_error = execute_query(sql, None, conn, cursor)
        if is_error:
            return is_error

    sql = ("SET FOREIGN_KEY_CHECKS = 1;")
    is_error = execute_query(sql, None, conn, cursor)
    if is_error:
        return is_error        

    close_connection(cursor, conn)               

    return success("OK")
