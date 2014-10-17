from flask import Blueprint, jsonify, request, Flask
from settings import mysql
from help_functions import *
from entities_info import *
from get_list_entities import *

user = Blueprint('user', __name__, url_prefix='/db/api/user')

@user.route('/create/', methods=['POST'])
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


@user.route('/details/', methods=['GET'])
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


@user.route('/follow/', methods=['POST'])
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


@user.route('/listFollowers/', methods=['GET'])
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


@user.route('/listFollowing/', methods=['GET'])
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


@user.route('/unfollow/', methods=['POST'])
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


@user.route('/updateProfile/', methods=['POST'])
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


@user.route('/listPosts/', methods=['GET'])
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