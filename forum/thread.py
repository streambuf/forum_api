from flask import Blueprint, jsonify, request, Flask
from settings import mysql
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
        return error_code(2, "Not found requried params", conn, cursor)

    conn = mysql.connect()
    cursor = conn.cursor()

    # Optional
    is_deleted = replace_null(request.json.get('isDeleted')) 

    # find forum_id
    sql = ("SELECT id FROM forum WHERE short_name = %s")
    data = [forum_short_name]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error 

    ret = cursor.fetchone()
    if ret:
        forum_id = ret[0]
    else:
        return error_code(1, 'forum not found', conn, cursor)        

    sql = ("INSERT INTO thread (title, message, slug, date, user_email, forum_id,"
        "isDeleted, isClosed, forum_sname) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data = [title, message, slug, date, user_email, forum_id, is_deleted, is_closed, forum_short_name]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    sql = ("select LAST_INSERT_ID() as post_id;")
    is_error = execute_query(sql, None, conn, cursor)
    if is_error:
        return is_error

    ret = cursor.fetchone()
    thread_id = ret[0] 

    close_connection(conn, cursor)

    return jsonify({'code': 0, 'response':
                {'date': date, 'forum': forum_short_name, 'id': thread_id,
                 'isClosed': is_closed, 'isDeleted': is_deleted, 'message': message,
                 'slug': slug, 'title': title, 'user': user_email}})


@thread.route('/details/', methods=['GET'])
def thread_details():
    # requried
    thread_id = request.args.get('thread')
    if thread_id is None:
        return  jsonify(code = 2, response = 'Not found requried params')
    # optional
    related = request.args.getlist('related')

      
    options = {}
    for rel in related:
        if rel == 'thread':
            return jsonify(code = 3, response = 'Error related' )
        options[rel] = True   

    resp = {}
    resp['code'] = 0
    resp['response'] = thread_info(thread_id, options) 

    if resp['response'] and resp['response'].get('code'):
        resp['code'] = resp['response'].get('code')
        resp['response'] = resp['response'].get('response')    

    return jsonify(resp)


@thread.route('/list/', methods=['GET'])
def thread_list():
    # requried
    user_email = request.args.get('user')
    forum = request.args.get('forum')
    
    # optional
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')

    return get_list_threads({"user_email": user_email, "forum": forum, "since": since,
        "limit": limit, "order": order})    


@thread.route('/close/', methods=['POST'])
def thread_close():
    # Requried
    try:
        thread_id = request.json['thread'] 
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET isClosed = 1 WHERE id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"thread": thread_id})


@thread.route('/open/', methods=['POST'])
def thread_open():
    # Requried
    try:
        thread_id = request.json['thread'] 
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET isClosed = 0 WHERE id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"thread": thread_id})


@thread.route('/remove/', methods=['POST'])
def thread_remove():
    # Requried
    try:
        thread_id = request.json['thread'] 
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET isDeleted = 1 WHERE id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"thread": thread_id})


@thread.route('/restore/', methods=['POST'])
def thread_restore():
    # Requried
    try:
        thread_id = request.json['thread'] 
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET isDeleted = 0 WHERE id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"thread": thread_id})


@thread.route('/subscribe/', methods=['POST'])
def thread_subscribe():
    # Requried
    try:
        thread_id = request.json['thread']
        email = request.json['user'] 
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("INSERT INTO subscriptions (user_email, thread_id) VALUES (%s, %s)")
    data = [email, thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"thread": thread_id, "user": email})


@thread.route('/unsubscribe/', methods=['POST'])
def thread_unsubscribe():
    # Requried
    try:
        thread_id = request.json['thread']
        email = request.json['user'] 
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("DELETE FROM subscriptions WHERE user_email = %s AND thread_id = %s")
    data = [email, thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"thread": thread_id, "user": email})    


@thread.route('/update/', methods=['POST'])
def thread_update():
    # Requried
    try:
        message = request.json['message'] 
        slug = request.json['slug']
        thread_id = request.json['thread']
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("UPDATE thread SET message = %s, slug = %s WHERE id = %s")
    data = [message, slug, thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = thread_info(thread_id))


@thread.route('/vote/', methods=['POST'])
def thread_vote():
    # Requried
    try:
        vote = request.json['vote']
        thread_id = request.json['thread']
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    if vote == 1:
        sql = ("UPDATE thread SET likes = likes + 1, points = points + 1 WHERE id = %s")
    else:
        sql = ("UPDATE thread SET dislikes = dislikes + 1, points = points - 1 WHERE id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = thread_info(thread_id))


@thread.route('/listPosts/', methods=['GET'])
def thread_list_posts():
    # requried
    thread_id = request.args.get('thread')
    
    # optional
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')
    sort = request.args.get('sort')

    return get_list_posts({"thread_id": thread_id, "since": since,
        "limit": limit, "order": order, "sort": sort}) 