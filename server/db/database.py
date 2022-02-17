import mysql.connector

from mysql.connector import Error

class MySQL:
    def __init__(self):
        self.connection = None

    def create_connection(self, host_name: str, user_name: str, user_password: str) -> bool:
        flag = True
        try:
            self.connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database="client_server"
            )
        except Error as e:
            flag = False

        return flag

    def stop_connection(self):
        self.connection.close()

    def select(self, query: str):
        self.connection.commit()
        if self.connection is None:
            return False
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result

    def insert(self, query: str, value: tuple):
        if self.connection is None:
            return False
        with self.connection.cursor() as cursor:
            cursor.execute(query, value)
        self.connection.commit()