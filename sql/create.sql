DROP DATABASE IF EXISTS forum_db;
CREATE DATABASE forum_db;
use forum_db;

CREATE TABLE user (
    id INT(11) NOT NULL,
    email VARCHAR(25) NOT NULL PRIMARY KEY,
    username VARCHAR(25),
    name VARCHAR(25),
    about TEXT,
    isAnonymous TINYINT(1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE user ADD INDEX c_email_id (email, id);

CREATE TABLE forum (
    id INT(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    name VARCHAR(35) NOT NULL UNIQUE,
    short_name VARCHAR(35) NOT NULL UNIQUE,
    user_email VARCHAR(25) NOT NULL,
    CONSTRAINT FOREIGN KEY (user_email) REFERENCES user (email),
    INDEX ishort_name (short_name),
    INDEX idate (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE thread (
    id INT(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    slug VARCHAR(50) NOT NULL,
    date DATETIME NOT NULL,
    isClosed TINYINT(1) DEFAULT 0,
    isDeleted TINYINT(1) DEFAULT 0,
    likes SMALLINT DEFAULT 0,
    dislikes SMALLINT DEFAULT 0,
    points SMALLINT DEFAULT 0,
    posts SMALLINT DEFAULT 0,    
    user_email VARCHAR(25) NOT NULL,
    forum_id INT(11) NOT NULL,
    forum_sname VARCHAR(35) NOT NULL,
    CONSTRAINT FOREIGN KEY (user_email) REFERENCES user (email),
    CONSTRAINT FOREIGN KEY (forum_id) REFERENCES forum (id),
    INDEX idate (date),
    INDEX iforum_sname (forum_sname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE thread ADD INDEX c_user_date (user_email, date);
ALTER TABLE thread ADD INDEX c_forum_date (forum_sname, date);

CREATE TABLE post (
    id INT(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    message TEXT NOT NULL,
    forum VARCHAR(35) NOT NULL,
    date DATETIME NOT NULL,
    isApproved TINYINT(1),
    isDeleted TINYINT(1),
    isEdited TINYINT(1),
    isHighlighted TINYINT(1),
    isSpam TINYINT(1),
    likes SMALLINT DEFAULT 0,
    dislikes SMALLINT DEFAULT 0,
    points SMALLINT DEFAULT 0,
    parent_id INT(11),
    user_email VARCHAR(25) NOT NULL,
    thread_id INT(11) NOT NULL,
    CONSTRAINT FOREIGN KEY (user_email) REFERENCES user (email),
    CONSTRAINT FOREIGN KEY (thread_id) REFERENCES thread (id),
    INDEX iforum (forum)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE post ADD INDEX c_forum_user (forum, user_email);
ALTER TABLE post ADD INDEX c_threadid_date (thread_id, date);
ALTER TABLE post ADD INDEX c_user_date (user_email, date);
ALTER TABLE post ADD INDEX c_forum_date (forum, date);

CREATE TABLE subscriptions (
    id INT(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_email VARCHAR(25) NOT NULL,
    thread_id INT(11) NOT NULL,    
    CONSTRAINT FOREIGN KEY (user_email) REFERENCES user (email),
    CONSTRAINT FOREIGN KEY (thread_id) REFERENCES thread (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE subscriptions ADD INDEX c_user_thread(user_email, thread_id);

CREATE TABLE followers (
    id INT(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_email VARCHAR(25) NOT NULL,
    follower_email VARCHAR(25) NOT NULL, 
    CONSTRAINT FOREIGN KEY (user_email) REFERENCES user (email),
    CONSTRAINT FOREIGN KEY (follower_email) REFERENCES user (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE followers ADD INDEX c_user_follower (user_email, follower_email);
ALTER TABLE followers ADD INDEX c_follower_user (follower_email, user_email);

DELIMITER $$

DROP TRIGGER IF EXISTS count_post$$
CREATE TRIGGER count_post BEFORE INSERT ON post
    FOR EACH ROW 
        BEGIN
            UPDATE thread SET posts = posts + 1 WHERE id = NEW.thread_id;
        END $$

DROP TRIGGER IF EXISTS thread_deleted$$
CREATE TRIGGER thread_deleted BEFORE UPDATE ON thread
    FOR EACH ROW 
        BEGIN
            IF NEW.isDeleted = true AND OLD.isDeleted = false THEN
                UPDATE post  SET isDeleted = True 
                WHERE thread_id = OLD.id;
            ELSEIF NEW.isDeleted = false AND OLD.isDeleted = true THEN
                UPDATE post  SET isDeleted = False 
                WHERE thread_id = OLD.id;
            END IF;
        END $$

/*DROP TRIGGER IF EXISTS post_deleted$$
CREATE TRIGGER post_deleted BEFORE UPDATE ON post
    FOR EACH ROW 
        BEGIN
                IF NEW.isDeleted = true AND OLD.isDeleted = false THEN
                    UPDATE thread  SET posts = posts - 1 
                    WHERE id = NEW.thread_id;
                ELSEIF NEW.isDeleted = false AND OLD.isDeleted = true THEN
                    UPDATE thread  SET posts = posts + 1 
                    WHERE id = NEW.thread_id;
                END IF;
           
        END $$*/
DELIMITER ;