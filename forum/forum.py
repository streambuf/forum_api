from flask import Blueprint, jsonify, request, Flask
from settings import mysql
from help_functions import *
from entities_info import *
from get_list_entities import *

forum = Blueprint('forum', __name__, url_prefix='/db/api/forum')

@forum.route('/create/', methods=['POST'])
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


@forum.route('/details/', methods=['GET'])
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


@forum.route('/listThreads/', methods=['GET'])
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


@forum.route('/listUsers/', methods=['GET'])
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


@forum.route('/listPosts/', methods=['GET'])
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