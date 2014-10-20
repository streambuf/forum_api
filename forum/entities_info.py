from settings import mysql, Codes
from help_functions import *
from datetime import datetime

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
        return {"code": Codes.not_found, "response": "Forum not found"}

    close_connection(conn, cursor)

    return {'id': ret[0], 'name': ret[1], 'short_name': ret[2], 'user': ret[3]}


def thread_info(thread_id, options = None):
    conn = mysql.connect()
    cursor = conn.cursor()

    if not is_number(thread_id):
        return {"code": Codes.incorrect_query, "response": "thread_id not digit"}

    sql = ("SELECT date, dislikes, forum_id, isClosed, isDeleted, likes,"
        " message, points, posts, slug, title, user_email, forum_sname FROM thread WHERE id = %s")
    data = [thread_id]
    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": Codes.unknown_error, "response": "execute exception for:" + sql}

    ret = cursor.fetchone()
    if ret is None:
        close_connection(conn, cursor)
        return {"code": Codes.not_found, "response": "Thread not found"}

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


def post_info(post_id, options = None):
    conn = mysql.connect()
    cursor = conn.cursor()

    if not is_number(post_id):
        return {"code": Codes.incorrect_query, "response": "post_id not digit"}

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
        return {"code": Codes.not_found, "response": "Thread not found"}

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


def user_info(user_email, options = None):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = ("SELECT id, username, name, email, about, isAnonymous FROM user WHERE email = %s")
    data = [user_email]
    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": Codes.unknown_error, "response": "execute exception for:" + sql}

    ret = cursor.fetchone()
    if ret is None:
        close_connection(conn, cursor)
        return {"code": Codes.not_found, "response": "User not found"}

    # subscriptions
    sql = ("SELECT thread_id FROM subscriptions WHERE user_email = %s")    
    data = [user_email]
    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": Codes.unknown_error, "response": "execute exception for:" + sql}

    subscriptions = get_array(cursor)

    sql = ("SELECT follower_email FROM followers WHERE user_email = %s")
    data = [user_email]     
    
    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": Codes.unknown_error, "response": "execute exception for:" + sql}

    followers = get_array(cursor)
    
    sql = ("SELECT user_email FROM followers WHERE follower_email = %s")
    data = [user_email]        

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        close_connection(conn, cursor)
        return {"code": Codes.unknown_error, "response": "execute exception for:" + sql}

    following = get_array(cursor)

    close_connection(conn, cursor)
            
    return { 'about': ret[4], 'email': ret[3], 'followers': followers,
        'following': following, 'id': ret[0], 'isAnonymous': bool(ret[5]), 'name': ret[2],
        'subscriptions': subscriptions, 'username': ret[1]}            