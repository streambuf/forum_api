from flask import Blueprint, jsonify, request, Flask
from settings import *
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
        return error_code(Codes.invalid_query, "Not found requried params", cursor)    

    cursor = conn.cursor()

    sql = ("INSERT INTO forum (name, short_name, user_email) VALUES (%s, %s, %s)")
    data = [name, short_name, user_email]

    is_error = execute_query(sql, data, cursor)
    if is_error:
        return error_code(Codes.not_found, 'user_email not found', cursor)

    forum_id = cursor.lastrowid 

    close_connection(cursor)

    return success({'id': forum_id, 'name': name, 'short_name': short_name, 'user': user_email })
#-------------------------------------------------------------------------------------------------


@forum.route('/details/', methods=['GET'])
def forum_details():
    related = request.args.getlist('related')
    forum = request.args.get('forum')

    if forum is None:
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')
      
    resp = {}
    resp['code'] = Codes.ok
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
    params = build_dict_params(request, ['forum', 'since', 'limit', 'order', 'sort'])
    related = request.args.getlist('related')
    
    options = {}
    for rel in related:
       options[rel] = True

    params['related'] = options   

    return get_list_threads(params) 
#-------------------------------------------------------------------------------------------------


@forum.route('/listUsers/', methods=['GET'])
def forum_list_users():
    params = build_dict_params(request, ['forum', 'since_id', 'limit', 'order'])
    params['user'] = params['forum']
              
    params['sql'] = ("SELECT DISTINCT user_email FROM post"
        " JOIN user ON post.user_email = user.email AND post.forum = %s")

    return get_list_users(params)
#-------------------------------------------------------------------------------------------------


@forum.route('/listPosts/', methods=['GET'])
def forum_list_posts():
    params = build_dict_params(request, ['forum', 'since', 'limit', 'order', 'sort'])
    related = request.args.getlist('related')

    options = {}
    for rel in related:
       options[rel] = True

    params['related'] = options   

    return get_list_posts(params) 