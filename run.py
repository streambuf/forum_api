# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, render_template
from datetime import datetime
from flaskext.mysql import MySQL
mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'drovosek'
app.config['MYSQL_DATABASE_DB'] = 'forum_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
app.debug = True

################### HELP FUNCTIONS ################################################
def execute_query(sql, data, conn, cursor):
    try:
        cursor.execute(sql, data)
        conn.commit()
    except:
        conn.rollback()
        error_info = error_code(4, 'execute exception for:' + sql, conn, cursor)
        return error_info
    return None    
#-------------------------------------------------------------------------------------------------


def error_code(code, response, conn, cursor):
    close_connection(conn, cursor)
    return jsonify(code = code, response = response)
#-------------------------------------------------------------------------------------------------


def close_connection(conn, cursor):
    cursor.close()
    conn.close()
#-------------------------------------------------------------------------------------------------


def get_array(cursor):
    array = []    
    rets = cursor.fetchall()
    for row in rets:
        array.append(row[0])
    return array
#-------------------------------------------------------------------------------------------------


def replace_null(param):
    if param is None:
        param = 'false'
    return param    
#-------------------------------------------------------------------------------------------------

def is_number(str):
    try:
        int(str)
        return True
    except ValueError:
        return False
#-------------------------------------------------------------------------------------------------            

################### FORUM VIEWS ################################################
def forum_info(forum):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ("SELECT id, name, short_name, user_email FROM forum WHERE short_name = %s")
    data = [forum]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    ret = cursor.fetchone()
    if ret is None:
        close_connection(conn, cursor)
        return {"code": 1, "response": "Forum not found"}

    close_connection(conn, cursor)

    return {'id': ret[0], 'name': ret[1], 'short_name': ret[2], 'user': ret[3]}
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/forum/create/', methods=['POST'])
def forum_create():
    try:
        name = request.json['name']
        short_name = request.json['short_name']
        user_email = request.json['user']
    except:
        return error_code(2, "Not found requried params", conn, cursor)    

    conn = mysql.connect()
    cursor = conn.cursor()
        
    # check on unique
    sql = ("SELECT id, user_email FROM forum WHERE short_name = %s")
    data = [short_name]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error 

    ret = cursor.fetchone()
    # if exists
    if ret:
        forum_id = ret[0]
        user_email = ret[1]
     # else create new forum        
    else:
        #check user
        sql = ("SELECT email FROM user WHERE email = %s")
        data = [user_email]

        is_error = execute_query(sql, data, conn, cursor)
        if is_error:
            return is_error 

        ret = cursor.fetchone()
        if ret is None:
            return error_code(1, 'user_email not found', conn, cursor)

        sql = ("INSERT INTO forum (name, short_name, date, user_email) VALUES (%s, %s, %s, %s)")
        data = [name, short_name, datetime.now(), user_email]

        is_error = execute_query(sql, data, conn, cursor)
        if is_error:
            return is_error

        sql = ("select LAST_INSERT_ID() as forum_id;")
        is_error = execute_query(sql, None, conn, cursor)
        if is_error:
            return is_error

        ret = cursor.fetchone()
        forum_id = ret[0] 

    close_connection(conn, cursor)

    return jsonify({'code': 0, 'response':
                {'id': forum_id, 'name': name, 'short_name': short_name, 'user': user_email }})
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/forum/details/', methods=['GET'])
def forum_details():
    related = request.args.getlist('related')
    forum = request.args.get('forum')

    if forum is None:
        return  jsonify(code = 2, response = 'Not found requried params')
      
    resp = {}
    resp['code'] = 0
    resp['response'] = forum_info(forum)

    if resp['response'] and resp['response'].get('code'):
        resp['code'] = resp['response'].get('code')
        resp['response'] = resp['response'].get('response')
           
    # user info
    elif related and related[0] == 'user':
        resp['response']['user'] = user_info(resp['response']['user']) 

     

    return jsonify(resp)
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/forum/listThreads/', methods=['GET'])
def forum_list_threads():
    # requried
    forum = request.args.get('forum')
    
    # optional
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')
    related = request.args.getlist('related')
    
    options = {}
    for rel in related:
       options[rel] = True 
              
    return get_list_threads({"forum": forum, "since": since,
        "limit": limit, "order": order, "related": options})
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/forum/listUsers/', methods=['GET'])
def forum_list_users():
    # requried
    forum = request.args.get('forum')
    
    # optional
    since_id = request.args.get('since_id')
    limit = request.args.get('limit')
    order = request.args.get('order')
              
    conn = mysql.connect()
    cursor = conn.cursor()

    if forum is None:
        return  jsonify(code = 2, response = 'Not found requried params')

    sql = ("SELECT DISTINCT user_email FROM post"
        " JOIN user ON post.user_email = user.email AND post.forum = %s")
    data = [forum]
    if since_id:
        sql = sql + " AND user.id >= %s"
        data.append(since_id)
    if order:
        sql = sql + " ORDER BY name " + order
    else:
         sql = sql + " ORDER BY name DESC"  
    if limit:
        sql = sql + " LIMIT %s"
        data.append(int(limit))    

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    array = []   
    rets = cursor.fetchall()
    for ret in rets:
        array.append(user_info(ret[0]))

    close_connection(conn, cursor)
          
    return jsonify(code = 0, response = array) 
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/forum/listPosts/', methods=['GET'])
def forum_list_posts():
    # requried
    forum = request.args.get('forum')
    
    # optional
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')
    sort = request.args.get('sort')
    related = request.args.getlist('related')
    
    options = {}
    for rel in related:
       options[rel] = True     

    return get_list_posts({"forum": forum, "since": since,
        "limit": limit, "order": order, "sort": sort, "related": options})              
################### END FORUM ###################################################      


################### THREAD VIEWS ################################################
def thread_info(thread_id, options = None):
    conn = mysql.connect()
    cursor = conn.cursor()

    if not is_number(thread_id):
        return {"code": 3, "response": "thread_id not digit"}

    sql = ("SELECT date, dislikes, forum_id, isClosed, isDeleted, likes,"
        " message, points, posts, slug, title, user_email, forum_sname FROM thread WHERE id = %s")
    data = [thread_id]
    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": 4, "response": "execute exception for:" + sql}

    ret = cursor.fetchone()
    if ret is None:
        close_connection(conn, cursor)
        return {"code": 1, "response": "Thread not found"}

    forum = ret[12]

    if options and options.get('forum'):
        forum = forum_info(forum)

    user = ret[11]        
            
    if options and options.get('user'):
        user = user_info(user)            

    close_connection(conn, cursor)
            
    return { 'date': ret[0].strftime("%Y-%m-%d %H:%M:%S"), 'dislikes': ret[1], 'forum': forum, 
        'id': int(thread_id),
        'isClosed': bool(ret[3]), 'isDeleted': bool(ret[4]), 'likes': ret[5], 'message': ret[6],
        'points': ret[7], 'posts': ret[8], 'slug': ret[9], 'title': ret[10], 'user': user}
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/create/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/details/', methods=['GET'])
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
#-------------------------------------------------------------------------------------------------


def get_list_threads(args):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ("SELECT date, dislikes, forum_id, isClosed, isDeleted, likes,"
        " message, points, posts, slug, title, user_email, forum_sname, id FROM thread WHERE")
    if args.get('user_email'):
        sql = sql + " user_email = %s"
        data = [args['user_email']]
    elif args.get('forum'):
        sql = sql + " forum_sname = %s"
        data = [args['forum']]
    else:    
        return  jsonify(code = 2, response = 'Not found requried params')

    if args.get('since'):
        sql = sql + " AND date >= %s"
        data.append(args['since'])
    if args.get('order'):
        sql = sql + " ORDER BY date " + args['order']
    else:
         sql = sql + " ORDER BY date DESC"  
    if args.get('limit'):
        sql = sql + " LIMIT %s"
        data.append(int(args['limit']))    

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    array = []   
    rets = cursor.fetchall()
    for ret in rets:
        forum = ret[12]
        user = ret[11]
        if args.get('related'):
            param = args.get('related')
            if param.get('user'):
                user = user_info(user)
            if param.get('forum'):
                forum = forum_info(forum)    
        array.append({ 'date': ret[0].strftime("%Y-%m-%d %H:%M:%S"), 'dislikes': ret[1],
        'forum': forum, 'id': ret[13],
        'isClosed': bool(ret[3]), 'isDeleted': bool(ret[4]), 'likes': ret[5], 'message': ret[6],
        'points': ret[7], 'posts': ret[8], 'slug': ret[9], 'title': ret[10], 'user': user})

    close_connection(conn, cursor)
          
    return jsonify(code = 0, response = array)
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/list/', methods=['GET'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/close/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/open/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/remove/', methods=['POST'])
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

    sql = ("SELECT id FROM post WHERE thread_id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    rets = cursor.fetchall()

    for ret in rets:
        sql = ("UPDATE post SET isDeleted = 1 WHERE id = %s")
        data = [ret[0]]

        is_error = execute_query(sql, data, conn, cursor)
        if is_error:
            return is_error


    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"thread": thread_id})
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/restore/', methods=['POST'])
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

    sql = ("SELECT id FROM post WHERE thread_id = %s")
    data = [thread_id]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    rets = cursor.fetchall()

    for ret in rets:
        sql = ("UPDATE post SET isDeleted = 0 WHERE id = %s")
        data = [ret[0]]

        is_error = execute_query(sql, data, conn, cursor)
        if is_error:
            return is_error    


    close_connection(conn, cursor)               

    return jsonify(code = 0, response = {"thread": thread_id})
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/subscribe/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/unsubscribe/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/update/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/vote/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/thread/listPosts/', methods=['GET'])
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
################### END Thread ##################################################



################### POST VIEWS ##################################################
def post_info(post_id, options = None):
    conn = mysql.connect()
    cursor = conn.cursor()

    if not is_number(post_id):
        return {"code": 3, "response": "post_id not digit"}

    sql = ("SELECT date, dislikes, forum, isApproved, isDeleted, isEdited,"
        " isHighlighted, isSpam, likes, message, parent_id, points, thread_id, user_email"
        " FROM post WHERE id = %s")
    data = [post_id]
    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": 4, "response": "execute exception for:" + sql}

    ret = cursor.fetchone()
    if ret is None:
        close_connection(conn, cursor)
        return {"code": 1, "response": "Thread not found"}

    forum = ret[2]

    if options and options.get('forum'):
        forum = forum_info(forum)

    thread = ret[12]        
            
    if options and options.get('thread'):
        thread = thread_info(thread)    
    user = ret[13]        
            
    if options and options.get('user'):
        user = user_info(user)            

    close_connection(conn, cursor)
            
    return {'date': ret[0].strftime("%Y-%m-%d %H:%M:%S"), 'dislikes': ret[1], 'forum': forum, 
            'id': int(post_id),
            'isApproved': bool(ret[3]), 'isDeleted': bool(ret[4]), 'isEdited': bool(ret[5]),
            'isHighlighted': bool(ret[6]), 'isSpam': bool(ret[7]), 'likes': ret[8], 'message': ret[9],
            'parent': ret[10], 'points': ret[11], 'thread': thread, 'user': user}
#-------------------------------------------------------------------------------------------------


def get_list_posts(args):
    conn = mysql.connect()
    cursor = conn.cursor()

    fields = ("date, dislikes, forum, isApproved, isDeleted, isEdited,"
        " isHighlighted, isSpam, likes, message, parent_id, points, thread_id,"
        " user_email, id, path, level")

    sql = "SELECT " + fields + " FROM post WHERE"

    if args.get('thread_id'):
        sql = sql + " thread_id = %s"
        data = [args['thread_id']]
    elif args.get('forum'):
        sql = sql + " forum = %s"
        data = [args['forum']]
    elif args.get('user_email'):
        sql = sql + " user_email = %s"
        data = [args['user_email']]    
    else:    
        return  jsonify(code = 2, response = 'Not found requried params')

    if args.get('since'):
        sql = sql + " AND date >= %s"
        data.append(args['since'])

    sort = args.get('sort')    

    if sort == 'tree':
        if args.get('order') == 'asc':
            sql = sql + " ORDER BY path asc"
        else:
             sql = sql + " ORDER BY SUBSTR(path, 8), SUBSTR(path, 1, 6) DESC"

    else:
        sort_type = ' date '         
        if sort == 'parent_tree':
            sql = sql + " AND parent_id IS NULL"
            sort_type = ' path '
                
        if args.get('order'):
            sql = sql + " ORDER BY" + sort_type + args['order']
        else:
             sql = sql + " ORDER BY" + sort_type + "DESC"  


    if args.get('limit'):
        sql = sql + " LIMIT %s"
        data.append(int(args['limit']))    

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    resp = []
    level = 0
    num_points = 0 
    
    rets = cursor.fetchall()

    #find childs
    if sort == 'parent_tree':
        temp_array = []
        for ret in rets:
            path = ret[15]

            sql = "SELECT " + fields + " FROM post WHERE path LIKE %s ORDER BY path"
            data = [path + '%']
            is_error = execute_query(sql, data, conn, cursor)
            
            if is_error:
                return is_error
            temp_array.extend(cursor.fetchall())
        rets = temp_array    

    for ret in rets:
        forum = ret[2]
        user = ret[13]
        thread = ret[12]
        if args.get('related'):
            param = args.get('related')
            if param.get('user'):
                user = user_info(user)
            if param.get('forum'):
                forum = forum_info(forum)
            if param.get('thread'):
                thread = thread_info(thread)

        post = {'date': ret[0].strftime("%Y-%m-%d %H:%M:%S"), 'dislikes': ret[1], 'forum': forum,
            'id': ret[14],
            'isApproved': bool(ret[3]), 'isDeleted': bool(ret[4]), 'isEdited': bool(ret[5]),
            'isHighlighted': bool(ret[6]), 'isSpam': bool(ret[7]), 'likes': ret[8], 'message': ret[9],
            'parent': ret[10], 'points': ret[11], 'thread': thread, 'user': user, 'path': ret[15],
            'childs': [], 'level': ret[16] }        
        
        if sort == 'tree' or sort == 'parent_tree':
            
            plevel = post["level"]
            if plevel == 0:
                cur_post = post
                parent_post = cur_post
                resp.append(parent_post)
                level = 1
            elif plevel == level:
                cur_post['childs'].append(post)
            elif plevel > level:
                cur_post = cur_post['childs'][-1]
                cur_post['childs'].append(post)
                level = level + 1;
            elif plevel < level:
                level = 0
                cur_post = parent_post
                while (plevel != level + 1):
                    cur_post = cur_post['childs'][-1]
                    level = level + 1
                cur_post['childs'].append(post)

        else:
            resp.append(post)

    close_connection(conn, cursor)
          
    return jsonify(code = 0, response = resp)
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/post/create/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/post/details/', methods=['GET'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/post/list/', methods=['GET'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/post/remove/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/post/restore/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/post/update/', methods=['POST'])
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
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/post/vote/', methods=['POST'])
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
################### END POST ##################################################    


################### USER VIEWS ##################################################
def user_info(user_email, options = None):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ("SELECT id, username, name, email, about, isAnonymous FROM user WHERE email = %s")
    data = [user_email]
    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": 4, "response": "execute exception for:" + sql}

    ret = cursor.fetchone()
    if ret is None:
        close_connection(conn, cursor)
        return {"code": 1, "response": "User not found"}

    # subscriptions
    sql = ("SELECT thread_id FROM subscriptions WHERE user_email = %s")    
    data = [user_email]
    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": 4, "response": "execute exception for:" + sql}

    subscriptions = get_array(cursor)

    # for listFollowers (limit, order, since_id)
    if options and options.get('followers'):
        sql = ("SELECT follower_email FROM followers"
            " JOIN user ON followers.follower_email = user.email AND user_email = %s")
        if options.get('since_id'):
            sql = sql + " AND user.id >= %s"
            data.append(options['since_id'])
        sql = sql + " ORDER BY name"     
        if options.get('order') == 'asc':   
            sql = sql + " ASC"
        else:
            sql = sql + " DESC"        
        if options.get('limit'):
            sql = sql + " LIMIT %s"
            data.append(int(options['limit']))
    else:
        sql = ("SELECT follower_email FROM followers WHERE user_email = %s")
        data = [user_email]     
           
    
    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": 4, "response": "execute exception for:" + sql}

    followers = get_array(cursor)

    # for listFollowing (limit, order, since_id)
    if options and options.get('following'):
        sql = ("SELECT user_email FROM followers"
            " JOIN user ON followers.user_email = user.email AND follower_email = %s")
        if options.get('since_id'):
            sql = sql + " AND user.id >= %s"
            data.append(options['since_id'])
        sql = sql + " ORDER BY name"     
        if options.get('order') == 'asc':   
            sql = sql + " ASC"
        else:
            sql = sql + " DESC"        
        if options.get('limit'):
            sql = sql + " LIMIT %s"
            data.append(int(options['limit']))
    else:
        sql = ("SELECT user_email FROM followers WHERE follower_email = %s")
        data = [user_email]        

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": 4, "response": "execute exception for:" + sql}

    following = get_array(cursor)

    close_connection(conn, cursor)
            
    return { 'about': ret[4], 'email': ret[3], 'followers': followers,
        'following': following, 'id': ret[0], 'isAnonymous': bool(ret[5]), 'name': ret[2],
        'subscriptions': subscriptions, 'username': ret[1]}        
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/user/create/', methods=['POST'])
def user_create():
    # Requried
    try:
        username = request.json['username']
        about = request.json['about'] 
        name = request.json['name']
        email = request.json['email']
    except:
        return jsonify(code = 2, response = 'Not found requried params')        
    
    conn = mysql.connect()
    cursor = conn.cursor()

    # Optional
    is_anonymous = replace_null(request.json.get('isAnonymous'))

    # find user_id
    sql = ("SELECT id FROM user WHERE email = %s")
    data = [email]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error 

    ret = cursor.fetchone()
    if ret:
        return error_code(5, 'This user already exists', conn, cursor) 
    else:
        sql = ("SELECT MAX(id) FROM user")
        cursor.execute(sql)
        conn.commit()
        ret = cursor.fetchone()
        # create id for user        
        if ret[0] is None:
            user_id = 1
        else:
            user_id = ret[0] + 1        
          
        sql = ("INSERT INTO user (id, username, about, name, email, isAnonymous)" 
                "VALUES (%s, %s, %s, %s, %s, %s)")
        data = [user_id, username, about, name, email, is_anonymous]

        is_error = execute_query(sql, data, conn, cursor)
        if is_error:
            return is_error

    close_connection(conn, cursor)

    return jsonify({'code': 0, 'response':
                {'about': about, 'email': email, 'id': user_id,
                 'isAnonymous': is_anonymous, 'name': name, 'username': username}})
#--------------------------------------------------------------------------------


@app.route('/db/api/user/details/', methods=['GET'])
def user_details():
    # Requried
    email = request.args.get('user')
    if email is None:
        return  jsonify(code = 2, response = 'Not found requried params')  

    resp = {}
    resp['code'] = 0
    resp['response'] = user_info(email)

    if resp['response'] and resp['response'].get('code'):
        resp['code'] = resp['response'].get('code')
        resp['response'] = resp['response'].get('response')         

    return jsonify(resp)
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/user/follow/', methods=['POST'])
def user_follow():
    # Requried
    try:
        follower = request.json['follower']
        followee = request.json['followee']
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    

    sql = ("SELECT id FROM followers WHERE user_email = %s AND follower_email = %s")
    data = [followee, follower]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error 

    ret = cursor.fetchone()
    if ret is None:
        sql = ("INSERT INTO followers (user_email, follower_email) VALUES (%s, %s)")
        data = [followee, follower]

        is_error = execute_query(sql, data, conn, cursor)
        if is_error:
            return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = user_info(follower))    
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/user/listFollowers/', methods=['GET'])
def user_listFollowers():
    # Requried
    email = request.args.get('user')
    if email is None:
        return  jsonify(code = 2, response = 'Not found requried params')       
    # Optional
    limit = request.args.get('limit')
    order = request.args.get('order')
    since_id = request.args.get('since_id')

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ("SELECT follower_email FROM followers"
        " JOIN user ON followers.follower_email = user.email AND user_email = %s")
    data = [email]
    if since_id:
        sql = sql + " AND user.id >= %s"
        data.append(since_id)
    if order:
        sql = sql + " ORDER BY name " + order
    else:
         sql = sql + " ORDER BY name DESC"  
    if limit:
        sql = sql + " LIMIT %s"
        data.append(int(limit))    

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    array = []   
    rets = cursor.fetchall()
    for ret in rets:
        array.append(user_info(ret[0]))

    close_connection(conn, cursor)    

    return jsonify(code = 0, response = array)
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/user/listFollowing/', methods=['GET'])
def user_listFollowing():
    # Requried
    email = request.args.get('user')
    if email is None:
        return  jsonify(code = 2, response = 'Not found requried params')       
    # Optional
    limit = request.args.get('limit')
    order = request.args.get('order')
    since_id = request.args.get('since_id')

    conn = mysql.connect()
    cursor = conn.cursor()
    sql = ("SELECT user_email FROM followers"
            " JOIN user ON followers.user_email = user.email AND follower_email = %s")
   
    data = [email]
    if since_id:
        sql = sql + " AND user.id >= %s"
        data.append(since_id)
    if order:
        sql = sql + " ORDER BY name " + order
    else:
         sql = sql + " ORDER BY name DESC"  
    if limit:
        sql = sql + " LIMIT %s"
        data.append(int(limit))    

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    array = []   
    rets = cursor.fetchall()
    for ret in rets:
        array.append(user_info(ret[0]))

    close_connection(conn, cursor)  

    return jsonify(code = 0, response = array)
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/user/unfollow/', methods=['POST'])
def user_unfollow():
    # Requried
    try:
        follower = request.json['follower']
        followee = request.json['followee']
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("DELETE FROM followers WHERE user_email = %s AND follower_email = %s")
    data = [followee, follower]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = user_info(follower))
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/user/updateProfile/', methods=['POST'])
def user_updateProfile():
    # Requried
    try:
        about = request.json['about'] 
        name = request.json['name']
        email = request.json['user']
    except:
        return  jsonify(code = 2, response = 'Not found requried params')

    conn = mysql.connect()
    cursor = conn.cursor()    
    
    sql = ("UPDATE user SET name = %s, about = %s WHERE email = %s")
    data = [name, about, email]

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = user_info(email))   
#-------------------------------------------------------------------------------------------------


@app.route('/db/api/user/listPosts/', methods=['GET'])
def user_list_posts():
    # requried
    user_email = request.args.get('user')
    
    # optional
    since = request.args.get('since')
    limit = request.args.get('limit')
    order = request.args.get('order')
    sort = request.args.get('sort')

    return get_list_posts({"user_email": user_email, "since": since,
        "limit": limit, "order": order, "sort": sort})     
#################### END VIEWS ##################################################

@app.route('/')
def hello():
    tml = "test.html"
    return render_template(tml)

if __name__ == '__main__':
    app.run() 


@app.route('/db/api/clear/', methods=['POST'])
def clear():
    conn = mysql.connect()
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

    close_connection(conn, cursor)               

    return jsonify(code = 0, response = "OK")
