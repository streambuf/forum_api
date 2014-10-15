INSERT INTO
    user (id, username, email, name, about, isAnonymous)
	VALUES
    ('1', 'max', 'max4@mail.ru', 'maxim', 'student', '0'),
    ('2', 'roma1', 'roma@mail.ru', 'roman', 'free', '0'),
    ('3', 'lena', 'lena@mail.ru', 'elena', 'worker', '0');

INSERT INTO
    forum (name, short_name, date, user_email)
	VALUES
    ('test', 'stest', '2014-09-20 12:12:12', 'max4@mail.ru'),
    ('test2', 'stest2', '2014-09-20 12:12:12', 'roma@mail.ru'),
    ('test3', 'stest3', '2014-09-20 12:12:12', 'lena@mail.ru');

INSERT INTO
    thread (title, message, slug, date, user_email, forum_id, forum_sname)
	VALUES
    ('thread1', 'message1', 'slug1', '2014-09-20 12:12:12', 'max4@mail.ru', '1', 'stest'),
    ('thread2', 'message2', 'slug2', '2014-09-20 12:12:12', 'max4@mail.ru', '1', 'stest');

INSERT INTO
    subscriptions (id, user_email, thread_id)
	VALUES
    ('1', 'max4@mail.ru', '1'),
    ('2', 'max4@mail.ru', '2'),
    ('3', 'roma@mail.ru', '1');

INSERT INTO
    post (message, forum, date, isApproved, isDeleted, isEdited, isHighlighted,
    isSpam, parent_id, path, level, user_email, thread_id)
	VALUES
    ('message', 'stest', '2014-09-20 12:12:12', null, 1, 1, 1, 1, null, '000001', 0, 'max4@mail.ru', 1),
    ('message', 'stest', '2014-09-20 12:12:12', null, 1, 1, 1, 1, 1, '000001.000001', 0, 'max4@mail.ru', 1),
    ('message', 'stest', '2014-09-20 12:12:12', null, 1, 1, 1, 1, 1, '000001.000012', 0, 'max4@mail.ru', 1),
    ('message', 'stest', '2014-09-20 12:12:12', null, 1, 1, 1, 1, 1, '000001.000006', 0, 'max4@mail.ru', 1),
    ('message', 'stest', '2014-09-20 12:12:12', null, 1, 1, 1, 1, 1, '000001.000011', 0, 'max4@mail.ru', 1);

INSERT INTO
    followers (id, user_email, follower_email)
	VALUES
    ('1', 'max4@mail.ru', 'roma@mail.ru'),
    ('2', 'max4@mail.ru', 'lena@mail.ru'),
    ('3', 'roma@mail.ru', 'max4@mail.ru');


select id, path, level, parent_id from post  WHERE parent_id is NULL ORDER BY path;

select path from post where path LIKE '000003%' ORDER by path;



