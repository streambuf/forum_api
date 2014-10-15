DROP DATABASE forum_db;
CREATE DATABASE forum_db;
use forum_db;

CREATE TABLE user (
    id INT(11) NOT NULL,
    email VARCHAR(25) NOT NULL PRIMARY KEY,
    username VARCHAR(25) NOT NULL,
    name VARCHAR(25) NOT NULL,
    about VARCHAR(35) NOT NULL,
    isAnonymous TINYINT(1),
    INDEX iname (name)
) ENGINE=InnoDB;

CREATE TABLE forum (
    id INT(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    name VARCHAR(35) NOT NULL UNIQUE,
    short_name VARCHAR(35) NOT NULL UNIQUE,
    date DATETIME NOT NULL,
    user_email VARCHAR(25) NOT NULL,
    CONSTRAINT FOREIGN KEY (user_email) REFERENCES user (email),
    INDEX ishort_name (short_name),
    INDEX idate (date)
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

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
    path VARCHAR(255) NOT NULL,
    level INT(11) NOT NULL,
    parent_id INT(11),
    user_email VARCHAR(25) NOT NULL,
    thread_id INT(11) NOT NULL,
    CONSTRAINT FOREIGN KEY (user_email) REFERENCES user (email),
    CONSTRAINT FOREIGN KEY (thread_id) REFERENCES thread (id),
    INDEX ipath (path),
    INDEX iforum (forum),
    INDEX idate (date)
) ENGINE=InnoDB;

CREATE TABLE subscriptions (
    id INT(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_email VARCHAR(25) NOT NULL,
    thread_id INT(11) NOT NULL,    
    CONSTRAINT FOREIGN KEY (user_email) REFERENCES user (email),
    CONSTRAINT FOREIGN KEY (thread_id) REFERENCES thread (id)
) ENGINE=InnoDB;

CREATE TABLE followers (
    id INT(11) AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_email VARCHAR(25) NOT NULL,
    follower_email VARCHAR(25) NOT NULL, 
    CONSTRAINT FOREIGN KEY (user_email) REFERENCES user (email),
    CONSTRAINT FOREIGN KEY (follower_email) REFERENCES user (email)
) ENGINE=InnoDB;

DELIMITER $$
DROP TRIGGER IF EXISTS count_post$$
CREATE TRIGGER count_post BEFORE INSERT ON post
    FOR EACH ROW 
        BEGIN
            UPDATE thread SET posts = posts + 1 WHERE id = NEW.thread_id;
        END $$
DELIMITER ;