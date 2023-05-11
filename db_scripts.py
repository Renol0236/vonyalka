import sqlite3
from math import floor
import time


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('Ошибка при чтении из БД')
        return []

    def getUser(self, username):
        try:
            self.__cur.execute(f"SELECT * FROM logins WHERE login = '{username}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Нет такого сука')
                return False

            return res
        except sqlite3.Error as e:
            print(' getUser Ошибка при чтении из БД в методе getUser:' + str(e))

        return False

    def getSameUser(self, username):
        self.__cur.execute(f"SELECT COUNT() as `count` FROM logins WHERE login LIKE '{username}'")
        res = self.__cur.fetchone()
        if res['count'] > 0:
            return False
        else:
            return True

    def addUser(self, username, email, password):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM logins WHERE login LIKE '{username}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Такой пользователь уже существует')
                return False

            self.__cur.execute('INSERT INTO logins VALUES(?,?,?)', (username, email, password))
            self.__db.commit()
        except sqlite3.Error as error:
            print('Ошибка при записи данных в БД в методе addUser: ' + str(error))
            return False

        return True

    def addPost(self, title, price, description, contact):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM posts WHERE title LIKE '{title}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Статья уже создана')
                return False

            tm = floor(time.time())
            self.__cur.execute('INSERT INTO posts VALUES(NULL,?,?,?,?,?)', (title, price, description, contact, tm))
            self.__db.commit()
        except sqlite3.Error as error:
            print('Ошибка при записи данных в БД в методе addPost: ' + str(error))
            return False

        return True

    def getPost(self, postid):
        try:
            self.__cur.execute(f"SELECT title, text, price, contact FROM posts WHERE id = {postid} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка в методе getPost: " +str(e))

        return (False,False,False,False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id,title,price FROM posts ORDER BY tm DESC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка при чтении из БД в методе getPostsAnonce: ' +str(e))

        return []