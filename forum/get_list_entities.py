from flask import jsonify, request, g
from settings import *
from help_functions import *
from entities_info import *
from datetime import datetime

def get_list_threads(args):
    conn = conn_pool.get_connection()
    cursor = conn.cursor()

    sql = ("SELECT date, dislikes, forum_id, isClosed, isDeleted, likes,"
        " message, points, posts, slug, title, user_email, forum_sname, id FROM thread WHERE")
    
    if args.get('user'):
        sql = sql + " user_email = %s"
        data = [args['user']]
    elif args.get('forum'):
        sql = sql + " forum_sname = %s"
        data = [args['forum']]
    else:    
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

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

    close_connection(cursor, conn)
          
    return success(array)


def get_list_posts(args):
    conn = conn_pool.get_connection()
    cursor = conn.cursor()

    fields = ("date, dislikes, forum, isApproved, isDeleted, isEdited,"
        " isHighlighted, isSpam, likes, message, parent_id, points, thread_id,"
        " user_email, id")

    sql = "SELECT " + fields + " FROM post WHERE"

    if args.get('thread'):
        sql = sql + " thread_id = %s"
        data = [args['thread']]
    elif args.get('forum'):
        sql = sql + " forum = %s"
        data = [args['forum']]
    elif args.get('user'):
        sql = sql + " user_email = %s"
        data = [args['user']]    
    else:    
        return  jsonify(code = Codes.invalid_query, response = 'Not found requried params')

    if args.get('since'):
        sql = sql + " AND date >= %s"
        data.append(args['since'])   
                
    if args.get('order'):
        sql = sql + " ORDER BY date " + args['order']
    else:
         sql = sql + " ORDER BY date " + "DESC"  

    if args.get('limit'):
        sql = sql + " LIMIT %s"
        data.append(int(args['limit']))    

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    resp = []
    
    rets = cursor.fetchall()

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
            'parent': ret[10], 'points': ret[11], 'thread': thread, 'user': user}        
        
        resp.append(post)

    close_connection(cursor, conn)
          
    return success(resp)    


def get_list_users(args):
    conn = conn_pool.get_connection()
    cursor = conn.cursor()

    sql = args.get('sql')

    data = [args.get('user')]
    if args.get('since_id'):
        sql = sql + " AND user.id >= %s"
        data.append(args.get('since_id'))
    if args.get('order'):
        sql = sql + " ORDER BY name " + args.get('order')
    else:
         sql = sql + " ORDER BY name DESC"  
    if args.get('limit'):
        sql = sql + " LIMIT %s"
        data.append(int(args.get('limit')))    

    is_error = execute_query(sql, data, conn, cursor)
    if is_error:
        return is_error

    array = []   
    rets = cursor.fetchall()
    
    for ret in rets:
        array.append(user_info(ret[0]))

    close_connection(cursor, conn)

    return success(array)

