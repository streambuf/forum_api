from flask import jsonify, request
from settings import mysql
from help_functions import *
from entities_info import *
from datetime import datetime

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