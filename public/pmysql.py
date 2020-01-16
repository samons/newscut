import pymysql
import configparser
import os

class pmy(object):
    conn = None

    def __init__(self):

        current_file_path=os.path.dirname(os.path.abspath(__file__))
        print(current_file_path)
        config = configparser.ConfigParser()
        config.read(current_file_path+"/../conf/config.ini")
        self.host = config.get("mysql", "host")
        self.user = config.get("mysql", "user")
        self.password = config.get("mysql", "password")
        self.database = config.get("mysql", "database")
        self.charset = config.get("mysql", "charset")
        self.port = config.get("mysql", "port")

    def connect(self):
        self.conn = pymysql.connect(host=self.host, port=int(self.port), user=self.user, password=self.password, db=self.database,
                            charset=self.charset)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def get_one(self, sql, params=()):
        result = None
        try:
            self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()
            self.close()
        except Exception as e:
            print(e)
        return result

    def get_all(self, sql, params=()):
        list_data = ()
        try:
            self.connect()
            self.cursor.execute(sql, params)
            list_data = self.cursor.fetchall()
            self.close()
        except Exception as e:
            print(e)
        return list_data

    def insert(self, sql, params=()):
        return self.__edit(sql, params)

    def update(self, sql, params=()):
        return self.__edit(sql, params)

    def delete(self, sql, params=()):
        return self.__edit(sql, params)

    def __edit(self, sql, params):
        count = 0
        try:
            self.connect()
            count = self.cursor.execute(sql, params)
            self.conn.commit()
            self.close()
        except Exception as e:
            print(e)
        return count