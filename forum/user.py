from flask import Blueprint, jsonify, request, Flask, g
from settings import *
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
        return jsonify(code = Codes.invalid_query, response = 'Not found requried params')        
    
    cursor = conn.cursor()

    # Optional
    is_anonymous = request.json.get('isAnonymous', False)

    sql = ("INSERT INTO user (id, username, about, name, email, isAnonymous)" 
            "VALUES (%s, %s, %s, %s, %s, %s)")
    data = [g.cur_user_id, username, about, name, email, is_anonymous]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return error_code(Codes.user_exists, 'This user already exists', cursor) 
    cur_user_id = cur_user_id + 1
    close_connection(cursor)

    return success(
                {'about': about, 'email': email, 'id': user_id,
                 'isAnonymous': is_anonymous, 'name': name, 'username': username})


@user.route('/details/', methods=['GET'])
def user_details():
    # Requried
    email = request.args.get('user')
    if email is None:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')  

    resp = {}
    resp['code'] = Codes.ok
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
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    

    sql = ("INSERT INTO followers (user_email, follower_email) VALUES (%s, %s)")
    data = [followee, follower]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    close_connection(cursor)               

    return success(user_info(follower))    


@user.route('/listFollowers/', methods=['GET'])
def user_listFollowers():
    params = build_dict_params(request, ['user', 'since_id', 'limit', 'order'])

    params["sql"] = ("SELECT follower_email FROM followers"
        " JOIN user ON followers.follower_email = user.email AND user_email = %s")
    
    return get_list_users(params)

@user.route('/listFollowing/', methods=['GET'])
def user_listFollowing():
    params = build_dict_params(request, ['user', 'since_id', 'limit', 'order'])

    params["sql"] = ("SELECT user_email FROM followers"
            " JOIN user ON followers.user_email = user.email AND follower_email = %s")
   
    return get_list_users(params)


@user.route('/unfollow/', methods=['POST'])
def user_unfollow():
    # Requried
    try:
        follower = request.json['follower']
        followee = request.json['followee']
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    
    
    sql = ("DELETE FROM followers WHERE user_email = %s AND follower_email = %s")
    data = [followee, follower]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    close_connection(cursor)               

    return success(user_info(follower))


@user.route('/updateProfile/', methods=['POST'])
def user_updateProfile():
    # Requried
    try:
        about = request.json['about'] 
        name = request.json['name']
        email = request.json['user']
    except:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    cursor = conn.cursor()    
    
    sql = ("UPDATE user SET name = %s, about = %s WHERE email = %s")
    data = [name, about, email]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return is_error

    close_connection(cursor)               

    return success(user_info(email))   


@user.route('/listPosts/', methods=['GET'])
def user_list_posts():
    return get_list_posts(build_dict_params(request, ['user', 'since', 'limit', 'order', 'sort']))