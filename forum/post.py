from flask import Blueprint, jsonify, request, Flask
from settings import mysql
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
        return error_code(2, "Not found requried params", conn, cursor)

    conn = mysql.connect()
    cursor = conn.cursor()            
    
    # Optional
    parent_id = request.json.get('parent')
    is_approved = replace_null(request.json.get('isApproved'))
    is_highlighted = replace_null(request.json.get('isHighlighted'))
    is_edited = replace_null(request.json.get('isEdited'))
    is_spam = replace_null(request.json.get('isSpam'))
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

    # create path
    num_digits = 6 # max nesting: 252 / 6 = 42  
    path = str(1).rjust(num_digits, '0')
    level = 0
    if parent_id:
        # find max child
        sql = ("SELECT MAX(path), level FROM post WHERE parent_id = %s")
        data = [parent_id]
        is_error = execute_query(sql, data, conn, cursor)
        if is_error:
            return is_error
        ret = cursor.fetchone()
        if ret and ret[0]:
           array = ret[0].split('.')
           path = ret[0][:-7] + '.' + str(int(array[-1]) + 1).rjust(num_digits, '0')
           level = ret[1]
        else: # else find parent    
            sql = ("SELECT path, level FROM post WHERE id = %s")
            data = [parent_id]
            is_error = execute_query(sql, data, conn, cursor)
            if is_error:
                return is_error
            ret = cursor.fetchone()
            if ret and ret[0]:
               path = ret[0] + '.' + str(1).rjust(num_digits, '0')
               level = ret[1] + 1
    else: # else find post with max path
        sql = ("SELECT MAX(path) FROM post where parent_id IS NULL")
        is_error = execute_query(sql, None, conn, cursor)
        if is_error:
            return is_error
        ret = cursor.fetchone()
        if ret and ret[0]:
           path = str(int(ret[0]) + 1).rjust(num_digits, '0')
              

    sql = ("INSERT INTO post (message, forum, date, isApproved, isDeleted, isEdited, isHighlighted,"
        "isSpam, parent_id, path, level, user_email, thread_id) VALUES"
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data = [message, forum_short_name, date, is_approved, is_deleted, is_edited, is_highlighted, is_spam,
            parent_id, path, level, user_email, thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    sql = ("select LAST_INSERT_ID() as post_id;")
    is_error = execute_query(sql, None, conn, cursor)
    if is_error:
        return is_error

    ret = cursor.fetchone()
    post_id = ret[0] 

    close_connection(conn, cursor)

    return jsonify({'code': 0, 'response':
                {'date': date, 'forum': forum_short_name, 'id': post_id,
                 'isApproved': is_approved, 'isDeleted': is_deleted, 'isEdited': is_edited,
                 'isHighlighted': is_highlighted, 'isSpam': is_spam, 'message': message,
                 'parent': parent_id, 'thread': thread_id, 'user': user_email}})


@post.route('/details/', methods=['GET'])
def post_details():
    # requried
    post_id = request.args.get('post')
    if post_id is None:
        return  jsonify(code = 2, response = 'Not found requried params')
    # optional
    related = request.args.getlist('related')
    
    options = {}
    for rel in related:
       options[rel] = True      

    resp = {}
    resp['code'] = 0
    resp['response'] = post_info(post_id, options)

    if resp['response'] and resp['response'].get('code'):
        resp['code'] = resp['response'].get('code')
        resp['response'] = resp['response'].get('response')

    print resp    
        
    return jsonify(resp)


@post.route('/list/', methods=['GET'])
def post_list():
    # requried
    thread_id = request.args.get('thread')
    forum = request.args.get('forum')
    
    # optional
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')
    sort = request.args.get('sort')

    return get_list_posts({"thread_id": thread_id, "forum": forum, "since": since,
        "limit": limit, "order": order, "sort": sort})


@post.route('/remove/', methods=['POST'])
def post_remove():
    # Requried
    try:
        post_id = request.json['post'] 
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
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

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"post": post_id}) 


@post.route('/restore/', methods=['POST'])
def post_restore():
    # Requried
    try:
        post_id = request.json['post'] 
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
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

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"post": post_id}) 


@post.route('/update/', methods=['POST'])
def post_update():
    # Requried
    try:
        message = request.json['message'] 
        post_id = request.json['post']
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("UPDATE post SET message = %s WHERE id = %s")
    data = [message, post_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = post_info(post_id))


@post.route('/vote/', methods=['POST'])
def post_vote():
    # Requried
    try:
        vote = request.json['vote']
        post_id = request.json['post']
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    if vote == 1:
        sql = ("UPDATE post SET likes = likes + 1, points = points + 1 WHERE id = %s")
    else:
        sql = ("UPDATE post SET dislikes = dislikes + 1, points = points - 1 WHERE id = %s")
    data = [post_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = post_info(post_id))