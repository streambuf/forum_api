#info
SELECT count(*) FROM post;
select * from post;
SELECT count(*) FROM thread;
SELECT count(*) FROM user;
SELECT * FROM forum where id = 1;

use forum_db;

EXPLAIN select SQL_NO_CACHE  * from post 
where forum='tqzf' AND date >= '2012-09-20 12:12:12' 
ORDER BY date DESC LIMIT 100;

SELECT SQL_NO_CACHE email FROM user WHERE EXISTS (
SELECT * FROM post WHERE forum = 'tqzf' AND user_email = user.email)
 AND user.id > 5 ORDER BY name LIMIT 67;

SELECT SQL_NO_CACHE email FROM user WHERE EXISTS (
SELECT DISTINCT user_email FROM post WHERE post.forum = 'tqzf')
ORDER BY name asc LIMIT 67;

EXPLAIN SELECT SQL_NO_CACHE DISTINCT user_email FROM post 
JOIN user ON post.user_email = user.email 
AND post.forum = 'tqzf' 
ORDER BY name asc LIMIT 67;

UPDATE thread SET posts = (SELECT COUNT(*) FROM post where thread_id = 1), isDeleted = 1 WHERE id = 1;
select * from thread where id = 1;

ALTER TABLE forum_db.post ENABLE KEYS;
ALTER TABLE forum_db.user ENABLE KEYS;
ALTER TABLE forum_db.thread ENABLE KEYS;

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