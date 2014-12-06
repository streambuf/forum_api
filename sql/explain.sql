#info
SELECT count(*) FROM post;
SELECT count(*) FROM thread;
SELECT count(*) FROM user;
SELECT count(*) FROM forum;


###user
# const
EXPLAIN SELECT SQL_NO_CACHE id FROM user WHERE email="twh89@list.ru";
#
EXPLAIN SELECT SQL_NO_CACHE id FROM followers 
WHERE user_email = "algx@list.ru" AND follower_email = "pyz9q1@mail.ru";
#
EXPLAIN SELECT SQL_NO_CACHE follower_email FROM followers
JOIN user ON followers.follower_email = user.email AND user_email = "algx@list.ru"
AND user.id >= 2 ORDER BY name ASC;
#
EXPLAIN SELECT SQL_NO_CACHE user_email FROM followers
JOIN user ON followers.user_email = user.email AND follower_email = "algx@list.ru";

EXPLAIN SELECT SQL_NO_CACHE thread_id FROM subscriptions WHERE user_email = "algx@list.ru";

#POST
EXPLAIN SELECT SQL_NO_CACHE id FROM forum WHERE short_name = 'lru';

EXPLAIN SELECT SQL_NO_CACHE * FROM post WHERE thread_id = 5 AND date>='2014-09-20 12:12:12';


#THREAD
EXPLAIN SELECT SQL_NO_CACHE id FROM subscriptions WHERE user_email = 'algx@list.ru' AND thread_id = 1;

EXPLAIN SELECT SQL_NO_CACHE date, dislikes, forum_id, isClosed, isDeleted, likes,
message, points, posts, slug, title, user_email, forum_sname FROM thread WHERE id = 5;




#FORUM
EXPLAIN SELECT id, name, short_name, user_email FROM forum WHERE short_name = 'eb';

EXPLAIN SELECT SQL_NO_CACHE DISTINCT user_email FROM post
JOIN user ON post.user_email = user.email AND post.forum = 'eb';