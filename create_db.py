from getpass import getpass
from mysql.connector import connect, Error

try:
    with connect(
        host="localhost",
        user=input("Имя пользователя: "),
        password=getpass("Пароль: "),
    ) as connection:
        create_db_query = "CREATE DATABASE client_server"
        with connection.cursor() as cursor:
            cursor.execute(create_db_query)
except Error as e:
    print(e)

try:
    with connect(
        host="localhost",
        user=input("Имя пользователя: "),
        password=getpass("Пароль: "),
        database="client_server",
    ) as connection:
        print(connection)
except Error as e:
    print(e)

create_users_table = """
CREATE TABLE Users( 
Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
Login CHAR(100) NOT NULL,
HashPass CHAR(255) NOT NULL
)
"""

with connection.cursor() as cursor:
    cursor.execute(create_users_table)
    connection.commit()

create_sessions_table = """
CREATE TABLE Sessions( 
Id INT NOT NULL PRIMARY KEY,
Nonse DATETIME,
NonseTS DATETIME,
FOREIGN KEY (Id) REFERENCES Users (Id) ON DELETE CASCADE
)
"""

with connection.cursor() as cursor:
    cursor.execute(create_sessions_table)
    connection.commit()
