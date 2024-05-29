import re
import psycopg2
from datetime import datetime
from psycopg2 import Error


class TDDB:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.authorised_user = None
        self.user_name = None
        self.open_connect()

    def open_connect(self):
        try:
            self.connection = psycopg2.connect(user="postgres", password="",
                                               host="127.0.0.1", port="5432", database="ToDoBase")
            self.cursor = self.connection.cursor()
            print("Соединение с PostgreSQL установлено")

        except (Exception, Error) as error:
            print("Ошибка при попытке подключения к PostgreSQL:", error)

    def close_connection(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Соединение с PostgreSQL закрыто")
        else:
            print("Соединение с PostgreSQL уже закрыто")

    # ---------------ЗАДАЧИ--------------

    def new_todo(self, text, deadline=None, important=False):
        regex1 = "\d\d/\d{2}/\d{4}"
        regex2 = "\d{4}/\d{2}/\d{2}"
        if deadline:
            if not (re.match(regex1, deadline) or re.match(regex2, deadline)):
                return False

        try:
            self.cursor.execute("""INSERT INTO todos (text_todos, id_users) VALUES (%s, %s) RETURNING id_todos""",
                                (str(text), self.authorised_user,))
            id = self.cursor.fetchone()[0]
            self.connection.commit()
            print("Запись внесена успешно")
            if deadline:
                self.cursor.execute(""" UPDATE todos SET deadline = %s WHERE id_todos=%s""", (str(deadline), id))
                self.connection.commit()
                #print("Дедлайн записи установлен")
            if important:
                self.cursor.execute(""" UPDATE todos SET important = %s WHERE id_todos=%s""", (bool(True), id))
                self.connection.commit()
                #print("Состояние записи \"важно\" применено успешно")
            return True

        except (Exception, Error) as error:
            print("Ошибка при внесении новой записи в PostgreSQL:", error)

    def select_all(self):
        try:
            if self.authorised_user is None:
                raise Error("Юзер не авторизован")
            self.cursor.execute("""SELECT * FROM todos WHERE id_users=%s ORDER BY id_todos ASC""",
                                (self.authorised_user,))
            records = list(self.cursor.fetchall())
            print("ВСЕ записи")
            return records
        except (Exception, Error) as error:
            print("Ошибка при доступе к записям в PostgreSQL:", error)

    def select_not_done_all(self):
        try:
            self.cursor.execute("""SELECT * FROM todos WHERE done=false AND id_users=%s ORDER BY id_todos ASC""",
                                (self.authorised_user,))  ###
            records = list(self.cursor.fetchall())
            print("НЕЗАВЕРШЕННЫЕ записи")
            return records
        except (Exception, Error) as error:
            print("Ошибка при доступе к невыполненным записям в PostgreSQL:", error)

    def select_done_all(self):
        try:
            self.cursor.execute("""SELECT * FROM todos WHERE done=true AND id_users=%s ORDER BY id_todos ASC""",
                                (self.authorised_user,))
            records = list(self.cursor.fetchall())
            print("ЗАВЕРШЕННЫЕ записи")
            return records
        except (Exception, Error) as error:
            print("Ошибка при доступе к невыполненным записям в PostgreSQL:", error)

    def select_deadline_all(self):
        result = []
        rows = self.select_not_done_all()
        for row in rows:
            if row[3] and is_deadline(row[3]):
                result.append(row)
        print("ГОРЯЩИЕ записи")
        return result

    def select_late_all(self):
        result = []
        rows = self.select_not_done_all()
        for row in rows:
            if row[3] and is_late(row[3]):
                result.append(row)
        print("ПРОСРОЧЕННЫЕ записи")
        return result

    def select_important_all(self):
        result = []
        rows = self.select_all()
        for row in rows:
            if row[4]:
                result.append(row)
        print("ВАЖНЫЕ записи")
        return result

    def select_by_text_all(self, text="", deadline=None):
        regex1 = "\d\d/\d{2}/\d{4}"
        regex2 = "\d{4}/\d{2}/\d{2}"
        if deadline:
            if not (re.match(regex1, deadline) or re.match(regex2, deadline)):
                return False
        try:
            query = """SELECT * FROM todos WHERE id_users=%s AND text_todos LIKE %s """
            if deadline:
                deadline_formatted = datetime.strptime(deadline, "%d/%m/%Y").strftime("%Y-%m-%d")
                query += """ AND deadline = %s ORDER BY id_todos ASC """
                self.cursor.execute(query, (self.authorised_user, f'%{text}%', deadline_formatted))
            else:
                query += """ ORDER BY id_todos ASC"""
                self.cursor.execute(query, (self.authorised_user, f'%{text}%',))
            records = list(self.cursor.fetchall())
            print("ТЕКСТ-ПОИСК записи")
            return records
        except (Exception, Error) as error:
            print("Ошибка при доступе к записям в PostgreSQL:", error)

    # def get_todo_by_id(self, id):  # for debug
    #     try:
    #         self.cursor.execute("""SELECT * FROM todos WHERE id_todos=%s""", (id,))
    #         records = list(self.cursor.fetchall())
    #         print(records)
    #         return records
    #     except (Exception, Error) as error:
    #         print("Ошибка при доступе к записи в PostgreSQL:", error)

    def update_todo_by_id(self, id, text, done=False, deadline=None, important=False):
        query = """UPDATE todos SET text_todos=%s, done=%s, important=%s WHERE id_todos=%s"""
        if done:
            d = "true"
        else:
            d = "false"
        if important:
            i = "true"
        else:
            i = "false"
        try:
            self.cursor.execute(query, (text, d, i, id))
            self.connection.commit()
            print("Изменение параметров записи прошло успешно")

        except (Exception, Error) as error:
            print("Ошибка при обновлении записи в PostgreSQL:", error)

        if deadline:
            try:
                self.cursor.execute("""UPDATE todos SET deadline=%s WHERE id_todos=%s""",
                                    (datetime.strptime(deadline, "%d/%m/%Y").strftime("%Y-%m-%d"), id))
                self.connection.commit()
                #print("Изменение date прошло успешно")

            except (Exception, Error) as error:
                print("Ошибка при обновлении записи в PostgreSQL:", error)

    def update_text_by_id(self, id, text):
        try:
            self.cursor.execute("""UPDATE todos SET text_todos=%s WHERE id_todos=%s""", (text, id))
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении записи в PostgreSQL:", error)

    def update_done_by_id(self, id, done):
        if done:
            d = 'true'
        else:
            d = 'false'
        try:
            self.cursor.execute("""UPDATE todos SET done=%s WHERE id_todos=%s""", (d, id))
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении записи в PostgreSQL:", error)

    def update_deadline_by_id(self, id, deadline="- -/- -/- - - -"):
        regex1 = "\d\d/\d{2}/\d{4}"
        regex2 = "\d{4}/\d{2}/\d{2}"
        try:
            if deadline == "- -/- -/- - - -":
                self.cursor.execute("""UPDATE todos SET deadline=NULL WHERE id_todos=%s""", (id,))
            elif not (re.match(regex1, deadline) or re.match(regex2, deadline)):
                return False
            else:
                self.cursor.execute("""UPDATE todos SET deadline=%s WHERE id_todos=%s""",
                                    (datetime.strptime(deadline, "%d/%m/%Y").strftime("%Y-%m-%d"), id))
            self.connection.commit()
            #print("Изменение date прошло успешно")
            return True
        except (Exception, Error) as error:
            print("Ошибка при обновлении записи в PostgreSQL:", error)

    def update_important_by_id(self, id, important):
        if important:
            i = 'true'
        else:
            i = 'false'
        try:
            self.cursor.execute("""UPDATE todos SET important=%s WHERE id_todos=%s""", (i, id))
            self.connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при обновлении записи в PostgreSQL:", error)

    def done_todo_by_id(self, id):
        try:
            self.cursor.execute("""UPDATE todos SET done = true WHERE id_todos=%s""", (id,))
            self.connection.commit()
            print("Состояние записи на \"завершено\" изменено успешно")

        except (Exception, Error) as error:
            print("Ошибка при изменении состояния записи в PostgreSQL:", error)

    def delete_todo_by_id(self, id):
        try:
            self.cursor.execute("""DELETE FROM todos WHERE id_todos=%s""", (id,))
            self.connection.commit()
            print("Запись удалена успешно")

        except (Exception, Error) as error:
            print("Ошибка при удалении записи в PostgreSQL:", error)

    # ---------------ПОЛЬЗОВАТЕЛИ--------------

    def new_user(self, name, login, password):
        try:
            self.cursor.execute("""INSERT INTO users (name, login, password) VALUES (%s, %s, %s) RETURNING id_users""",
                                (str(name), str(login), str(password),))
            self.connection.commit()
            print("Юзер создан успешно")

        except (Exception, Error) as error:
            print("Ошибка при создании нового пользователя в PostgreSQL:", error)

    def user_exist(self, login):
        try:
            self.cursor.execute("""SELECT * FROM users WHERE login=%s""", (str(login),))
            records = list(self.cursor.fetchall())
            return records != []
        except (Exception, Error) as error:
            print("Ошибка при проверке наличия логина в PostgreSQL:", error)

    def auth_user(self, login, password):
        try:
            self.cursor.execute("""SELECT * FROM users WHERE login=%s AND password=%s""", (str(login), str(password),))
            records = list(self.cursor.fetchall())
            if records:
                self.authorised_user = records[0][0]
                self.user_name = records[0][3]
            else:
                raise Error("Не существует пользователя с данным логином или пароль не верный")
        except (Exception, Error) as error:
            print("Ошибка при авторизации пользователя в PostgreSQL:", error)

    def exit_user(self):
        self.user_name = None
        self.authorised_user = None

    def delete_user(self, login):
        try:
            self.cursor.execute("""DELETE FROM users WHERE login=%s""", (str(login)))
            self.connection.commit()
            print("Пользователь удалён успешно")
        except (Exception, Error) as error:
            print("Ошибка при удалении пользователя в PostgreSQL:", error)

    # def get_user_info_by_id(self, id):  # for debug
    #     try:
    #         self.cursor.execute("""SELECT * FROM users WHERE id_users=%s""", (id,))
    #         records = list(self.cursor.fetchall())
    #         print(records)
    #         return records
    #     except (Exception, Error) as error:
    #         print("Ошибка при доступе к пользователю в PostgreSQL:", error)


# ------------ФУНКЦИИ ДЛЯ ВЗАИМОДЕЙСТВИЯ С ДАТАМИ-------------------

def is_deadline(d):
    if d == "- -/- -/- - - -":
        return False
    return (datetime.today().date() - d).days == 0 or (datetime.today().date() - d).days == -1


def is_late(d):
    if d == "- -/- -/- - - -":
        return False
    return (datetime.today().date() - d).days > 0


def today():
    return datetime.today().strftime("%d/%m/%Y")


def perform_date(date_from_bd=None):
    if date_from_bd:
        return date_from_bd.strftime("%d/%m/%Y")
    else:
        return "- -/- -/- - - -"
