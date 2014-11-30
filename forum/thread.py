from flask import Blueprint, jsonify, request, Flask
from settings import *
from help_functions import *
from entities_info import *
from get_list_entities import *

thread = Blueprint('thread', __name__, url_prefix='/db/api/thread')

@thread.route('/create/', methods=['POST'])
def thread_create():
    # Requried
    try:
        date = request.json['date']
        slug = request.json['slug'] 
        title = request.json['title']
        is_closed = request.json['isClosed']    
        message = request.json['message']
        user_email = request.json['user']
        forum_short_name = request.json['forum']
    except:
        return error_code(Codes.invalid_query, "Not found requried params", cursor)

    cursor = conn.cursor()

    # Optional
    is_deleted = request.json.get('isDeleted', False) 

    # find forum_id
    sql = ("SELECT id FROM forum WHERE short_name = %s")
    data = [forum_short_name]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error 

    ret = cursor.fetchone()
    if ret:
        forum_id = ret[0]
    else:
        return error_code(Codes.not_found, 'forum not found', cursor)        

    sql = ("INSERT INTO thread (title, message, slug, date, user_email, forum_id,"
        "isDeleted, isClosed, forum_sname) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data = [title, message, slug, date, user_email, forum_id, is_deleted, is_closed, forum_short_name]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    thread_id = cursor.lastrowid

    close_connection(cursor)

    return success(
                {'date': date, 'forum': forum_short_name, 'id': thread_id,
                 'isClosed': is_closed, 'isDeleted': is_deleted, 'message': message,
                 'slug': slug, 'title': title, 'user': user_email})


@thread.route('/details/', methods=['GET'])
def thread_details():
    # requried
    thread_id = request.args.get('thread')
    if thread_id is None:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')
    # optional
    related = request.args.getlist('related')

    options = {}
    for rel in related:
        if rel == 'thread':
            return jsonify(code = Codes.incorrect_query, response = 'Error related' )
        options[rel] = True   

    resp = {}
    resp['code'] = Codes.ok
    resp['response'] = thread_info(thread_id, options) 

    if resp['response'] and resp['response'].get('code'):
        resp['code'] = resp['response'].get('code')
        resp['response'] = resp['response'].get('response')    

    return jsonify(resp)


@thread.route('/list/', methods=['GET'])
def thread_list():
    return get_list_threads(build_dict_params(request, ['user', 'forum', 'since', 'limit', 'order', 'sort']))       


@thread.route('/close/', methods=['POST'])
def thread_close():
    # Requried
    try:
        thread_id = request.json['thread'] 
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET isClosed = 1 WHERE id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    close_connection(cursor)               

    return success({"thread": thread_id})


@thread.route('/open/', methods=['POST'])
def thread_open():
    # Requried
    try:
        thread_id = request.json['thread'] 
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET isClosed = 0 WHERE id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    close_connection(cursor)               

    return success({"thread": thread_id})


@thread.route('/remove/', methods=['POST'])
def thread_remove():
    # Requried
    try:
        thread_id = request.json['thread'] 
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET isDeleted = 1 WHERE id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    sql = ("UPDATE post SET isDeleted = 1 WHERE thread_id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error    


    close_connection(cursor)               

    return success({"thread": thread_id})


@thread.route('/restore/', methods=['POST'])
def thread_restore():
    # Requried
    try:
        thread_id = request.json['thread'] 
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET isDeleted = 0 WHERE id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    sql = ("UPDATE post SET isDeleted = 0 WHERE thread_id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error 

    close_connection(cursor)               

    return success({"thread": thread_id})


@thread.route('/subscribe/', methods=['POST'])
def thread_subscribe():
    # Requried
    try:
        thread_id = request.json['thread']
        email = request.json['user'] 
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    
    
    sql = ("INSERT INTO subscriptions (user_email, thread_id) VALUES (%s, %s)")
    data = [email, thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    close_connection(cursor)               

    return success({"thread": thread_id, "user": email})


@thread.route('/unsubscribe/', methods=['POST'])
def thread_unsubscribe():
    # Requried
    try:
        thread_id = request.json['thread']
        email = request.json['user'] 
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    
    
    sql = ("DELETE FROM subscriptions WHERE user_email = %s AND thread_id = %s")
    data = [email, thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    close_connection(cursor)               

    return success({"thread": thread_id, "user": email})    


@thread.route('/update/', methods=['POST'])
def thread_update():
    # Requried
    try:
        message = request.json['message'] 
        slug = request.json['slug']
        thread_id = request.json['thread']
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET message = %s, slug = %s WHERE id = %s")
    data = [message, slug, thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    close_connection(cursor)               

    return success(thread_info(thread_id))


@thread.route('/vote/', methods=['POST'])
def thread_vote():
    # Requried
    try:
        vote = request.json['vote']
        thread_id = request.json['thread']
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()  

    sql = sql = "UPDATE thread SET"  

    if vote == 1:
        sql = sql + " likes = likes + 1, points = points + 1"
    else:
        sql = sql + " dislikes = dislikes + 1, points = points - 1"

    sql = sql + " WHERE id = %s"    
    data = [thread_id]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    close_connection(cursor)               

    return success(thread_info(thread_id))


@thread.route('/listPosts/', methods=['GET'])
def thread_list_posts():
    return get_list_posts(build_dict_params(request, ['thread', 'since', 'limit', 'order', 'sort']))