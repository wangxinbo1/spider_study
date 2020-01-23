# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：study_start -> mysql
@IDE    ：PyCharm
@Author ：Mr. wang
@Date   ：2020/1/4 0004 15:09
@Desc   ：
=================================================='''
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import pooling
import time
import re
from mysql.connector.cursor import MySQLCursorDict

class MysqlManage():

    db_info = {
        "host":"localhost",  # 数据库主机地址
        "user":"root",  # 数据库用户名
        "passwd":"123456",  # 数据库密码
        "database":"smth"
    }

    TABLES = {}
    TABLES['topic'] = (
        "CREATE TABLE `topic` ("
        "  `id` int AUTO_INCREMENT,"
        "  `title` varchar(128) NOT NULL,"
        "  `url` varchar(1024) NOT NULL,"
        "  `author_id` varchar(32) NOT NULL,"
        "  `author_url` varchar(32) NOT NULL,"
        "  `status` varchar(32) NOT NULL DEFAULT 'new',"
        "  `rating` int NOT NULL DEFAULT 0,"
        "  `like_cnt` int NOT NULL DEFAULT 0,"
        "  `reply_cnt` int NOT NULL DEFAULT 0,"
        "  `publish_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "  `queue_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "  `done_time` timestamp NOT NULL DEFAULT '1970-01-02 00:00:00' ON UPDATE CURRENT_TIMESTAMP,"
        "  PRIMARY KEY (`id`),"
        "  UNIQUE (`url`)"
        ") ENGINE=InnoDB")

    TABLES['board'] = (
        "CREATE TABLE `board` ("
        "  `name` varchar(64) NOT NULL,"
        "  `url` varchar(1024) NOT NULL,"
        "  `mgr_id` varchar(32) NOT NULL,"
        "  `mgr_url` varchar(512) NOT NULL,"
        "  `topics_cnt` int(11) NOT NULL,"
        "  `posts_cnt` int(11) NOT NULL,"
        "  PRIMARY KEY (`name`),"
        "  UNIQUE (`url`)"
        ") ENGINE=InnoDB")

    TABLES['post'] = (
        "CREATE TABLE `post` ("
        "  `topic_id` varchar(16) NOT NULL,"
        "  `content` varchar(10240) NOT NULL DEFAULT '',"
        "  `post_index` int NOT NULL DEFAULT 0,"
        "  UNIQUE(`topic_id`, `post_index`) "
        ") ENGINE=InnoDB")

    # TABLES['post'] = ("CREATE TABLE post(topic_id varchar(16) NOT NULL,content varchar(10240) NOT NULL DEFAULT '',post_index int NOT NULL DEFAULT 0) ENGINE=InnoDB")

    def __init__(self):
        try:
            conn = mysql.connector.connect(
                host=self.db_info["host"],  # 数据库主机地址
                user=self.db_info["user"],  # 数据库用户名
                passwd=self.db_info["passwd"],  # 数据库密码
                # database=self.db_info["database"]  #要连接的数据库
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print('Create Error ' + err.msg)
            exit(1)

        mycursor = conn.cursor(cursor_class=MySQLCursorDict)

        try:
            conn.database=self.db_info["database"]
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.create_database(mycursor)
                conn.database=self.db_info["database"]
                self.create_table(mycursor)
            else:
                print(err)
                exit(1)
        finally:
            mycursor.close()
            conn.close()

        self.conn_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",
                                                                 pool_size=5,
                                                                 **self.db_info)

    def create_database(self,cursor):
        try:
            cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET utf8 ".format(self.db_info["database"]))

        except mysql.connector.Error as err:
            print("create database fail",err)
            exit(1)
        else:
            print("create database success")

    def create_table(self,cursor):
        for name,ddl in self.TABLES.items():
            try:
                cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("表已经存在")
                else:
                    print('create tables error ' + err.msg)
            else:
                print("create table success")

    def insert_board(self,board):
        conn=self.conn_pool.get_connection()
        cursor = conn.cursor()
        try:
            sql = ("INSERT INTO board(url, name, mgr_id, mgr_url, topics_cnt, posts_cnt)"
            "VALUES ('{}', '{}', '{}', '{}', {}, {} )").format(
            board['url'], board['name'], board['mgr_id'],
            board['mgr_url'], board['topics_cnt'], board['posts_cnt'])
            cursor.execute(sql)
            conn.commit()
        except mysql.connector.Error as err:
            print('insert_board() ' + err.msg)
            # print("Aready exist!")
            return
        finally:
            cursor.close()
            conn.close()

    def insert_topic(self,topic):
        conn=self.conn_pool.get_connection()
        cursor = conn.cursor()
        try:
            if re.match('\d\d\:\d\d:\d\d', topic['publish_time']):
                topic['publish_time'] = (time.strftime("%Y-%m-%d ", time.localtime()) + topic['publish_time']).strip()
            sql = ("INSERT INTO topic(title, url, author_id, author_url, publish_time,"
                   "rating, like_cnt, reply_cnt) "
                   "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}' )").format(
                topic['title'], topic['url'], topic['author_id'],
                topic['author_url'], topic['publish_time'], topic['rating'],
                topic['like_cnt'], topic['reply_cnt'])
            # print(sql)
            cursor.execute((sql))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print('insert_topic() ' + err.msg)
        # print("Aready exist!")
            return False
        finally:
            cursor.close()
            conn.close()

    def insert_post(self,post):
        conn=self.conn_pool.get_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO post(topic_id, content, post_index) VALUES ('{}', '{}', '{}' )".format(
                post['topic_id'], post['content'], post['post_index'])
            # print(sql)
            cursor.execute((sql))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print('insert_post() ' + err.msg)
            # print("Aready exist!")
            return False
        finally:
            cursor.close()
            conn.close()

    def dequeue_topic(self):
        conn = self.conn_pool.get_connection()
        cursor = conn.cursor(cursor_class=MySQLCursorDict)
        try:
            conn.start_transaction()
            cons = str(time.time())[4:]
            update_sql = "update topic set status='{}' where status='new' limit 1".format(cons)
            # print(sql)
            cursor.execute(update_sql)
            conn.commit()

            query = ("SELECT url, id FROM topic WHERE status='{}'".format(cons))
            cursor.execute(query)
            row = cursor.fetchone()
            if row is None:
                return None
            return row
        except mysql.connector.Error as err:
            print('dequeue_topic() ' + err.msg)
            # print("Aready exist!")
            return None
        finally:
            cursor.close()
            conn.close()

    def dequeue_batch_topics(self, size):
        con = self.conn_pool.get_connection()
        cursor = con.cursor(dictionary=True)
        try:
            con.start_transaction()
            const_id = ("%.9f" % time.time())[4:]
            update_query = ("UPDATE topic SET status='{}' WHERE status='new' LIMIT {}".format(const_id, size))
            cursor.execute(update_query)
            con.commit()

            query = ("SELECT url, id FROM topic WHERE status='{}'".format(const_id))
            cursor.execute(query)

            rows = cursor.fetchall()
            if rows is None:
                return None
            return rows
        except mysql.connector.Error as err:
            print('dequeueUrl() ' + err.msg)
            return None
        finally:
            cursor.close()
            con.close()

    def finish_topic(self, index):
        con = self.conn_pool.get_connection()
        cursor = con.cursor()
        try:
            # we don't need to update done_time using time.strftime('%Y-%m-%d %H:%M:%S') as it's auto updated
            update_query = ("UPDATE topic SET `status`='done' WHERE `id`=%d") % (index)
            cursor.execute(update_query)
            con.commit()
        except mysql.connector.Error as err:
            # print('finishUrl() ' + err.msg)
            return
        finally:
            cursor.close()
            con.close()







if __name__=="__main__":
    pass
    mm = MysqlManage()


