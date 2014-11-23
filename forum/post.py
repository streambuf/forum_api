from flask import Blueprint, jsonify, request, Flask, g
from settings import *
from help_functions import *
from entities_info import *
from get_list_entities import *

post = Blueprint('post', __name__, url_prefix='/db/api/post')

@post.route('/create/', methods=['POST'])
def post_create():
    # Requried
    try:
        date = request.json['date']
        thread_id = request.json['thread']    
        message = request.json['message']
        user_email = request.json['user']
        forum_short_name = request.json['forum']
    except:
        return error_code(Codes.invalid_query, "Not found requried params", conn, cursor)

    conn = conn_pool.get_connection()
    cursor = conn.cursor()            
    
    # Optional
    parent_id = request.json.get('parent')
    is_approved = request.json.get('isApproved', False)
    is_highlighted = request.json.get('isHighlighted', False)
    is_edited = request.json.get('isEdited', False)
    is_spam = request.json.get('isSpam', False)
    is_deleted = request.json.get('isDeleted', False)

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
        return error_code(Codes.not_found, 'forum not found', conn, cursor)   

    sql = ("INSERT INTO post (message, forum, date, isApproved, isDeleted, isEdited, isHighlighted,"
        "isSpam, parent_id, user_email, thread_id) VALUES"
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data = [message, forum_short_name, date, is_approved, is_deleted, is_edited, is_highlighted, is_spam,
            parent_id, user_email, thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    sql = ("select LAST_INSERT_ID() as post_id;")
    is_error = execute_query(sql, None, conn, cursor)
    if is_error:
        return is_error

    ret = cursor.fetchone()
    post_id = ret[0] 

    close_connection(cursor, conn)

    return success(
                {'date': date, 'forum': forum_short_name, 'id': post_id,
                 'isApproved': is_approved, 'isDeleted': is_deleted, 'isEdited': is_edited,
                 'isHighlighted': is_highlighted, 'isSpam': is_spam, 'message': message,
                 'parent': parent_id, 'thread': thread_id, 'user': user_email})


@post.route('/details/', methods=['GET'])
def post_details():
    # requried
    post_id = request.args.get('post')
    if post_id is None:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')
    # optional
    related = request.args.getlist('related')
    
    options = {}
    for rel in related:
       options[rel] = True      

    resp = {}
    resp['code'] = Codes.ok
    resp['response'] = post_info(post_id, options)

    if resp['response'] and resp['response'].get('code'):
        resp['code'] = resp['response'].get('code')
        resp['response'] = resp['response'].get('response')

    print resp    
        
    return jsonify(resp)


@post.route('/list/', methods=['GET'])
def post_list():
    return get_list_posts(build_dict_params(request, ['thread', 'forum', 'since', 'limit', 'order', 'sort']))


@post.route('/remove/', methods=['POST'])
def post_remove():
    # Requried
    try:
        post_id = request.json['post'] 
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    conn = conn_pool.get_connection()
    cursor = conn.cursor()    
    
    sql = ("UPDATE post SET isDeleted = 1 WHERE id = %s")
    data = [post_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    sql = ("SELECT thread_id FROM post WHERE id = %s")
    data = [post_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error
        
    ret = cursor.fetchone()        

    sql = ("UPDATE thread SET posts = posts - 1 WHERE id = %s")
    data = [ret[0]]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error    

    close_connection(cursor, conn)               

    return success({"post": post_id}) 


@post.route('/restore/', methods=['POST'])
def post_restore():
    # Requried
    try:
        post_id = request.json['post'] 
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    conn = conn_pool.get_connection()
    cursor = conn.cursor()    
    
    sql = ("UPDATE post SET isDeleted = 0 WHERE id = %s")
    data = [post_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    sql = ("SELECT thread_id FROM post WHERE id = %s")
    data = [post_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error
        
    ret = cursor.fetchone()        

    sql = ("UPDATE thread SET posts = posts + 1 WHERE id = %s")
    data = [ret[0]]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error    

    close_connection(cursor, conn)               

    return success({"post": post_id}) 


@post.route('/update/', methods=['POST'])
def post_update():
    # Requried
    try:
        message = request.json['message'] 
        post_id = request.json['post']
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    conn = conn_pool.get_connection()
    cursor = conn.cursor()    
    
    sql = ("UPDATE post SET message = %s WHERE id = %s")
    data = [message, post_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(cursor, conn)               

    return success(post_info(post_id))


@post.route('/vote/', methods=['POST'])
def post_vote():
    # Requried
    try:
        vote = request.json['vote']
        post_id = request.json['post']
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    conn = conn_pool.get_connection()
    cursor = conn.cursor()    
    
    sql = sql = "UPDATE post SET"  

    if vote == 1:
        sql = sql + " likes = likes + 1, points = points + 1"
    else:
        sql = sql + " dislikes = dislikes + 1, points = points - 1"

    sql = sql + " WHERE id = %s"    
    data = [post_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(cursor, conn)               

    return success(post_info(post_id))