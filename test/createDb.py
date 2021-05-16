
from getpass import getpass
from mysql.connector import connect, Error

DB_USER = "root"
DB_PSWD = "root"

def do_query(connection,query):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit() 
    except Error as e:
        print(e)

try:
    with connect(
        host="localhost",
        user=DB_USER,
        password=DB_PSWD,
        database="fitness",
    ) as connection:
        print(connection)

        do_query(connection, "DROP TABLE PAYMENT_ACTIONS")
        do_query(connection, "DROP TABLE ACTIONS")
        do_query(connection, "DROP TABLE USERS")
        do_query(connection, "DROP TABLE SCHEDULE")
        do_query(connection, "DROP TABLE COACHES")


        create_train_query = """
        CREATE TABLE SCHEDULE(
            ID INT AUTO_INCREMENT PRIMARY KEY,
            NAME VARCHAR(64) UNIQUE,
            START_TIME TIME,
            END_TIME TIME,
            TRAIN_AMOUNT INT
        );
        """
        create_users_query = """
        CREATE TABLE USERS(
            ID INT AUTO_INCREMENT PRIMARY KEY,
            RFID VARCHAR(8) UNIQUE,
            NAME VARCHAR(64),
            TEL_NUMBER VARCHAR(16),
            SCHEDULE_ID INT,
            START_DATE DATE,
            END_DATE DATE,
            TRAIN_AMOUNT INT,
            REGISTERED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            USER_LEVEL INT,
            FOREIGN KEY(SCHEDULE_ID) REFERENCES SCHEDULE(ID)
        );
        """
        create_actions_query = """
        CREATE TABLE ACTIONS(
            ID INT AUTO_INCREMENT PRIMARY KEY,
            USER_ID INT,
            ACTION_TYPE TINYINT,
            ACTION_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            FOREIGN KEY(USER_ID) REFERENCES USERS(ID)
        );
        """
        create_coaches_query = """
        CREATE TABLE COACHES(
            ID INT AUTO_INCREMENT PRIMARY KEY,
            NAME VARCHAR(64)
        );
        """
        create_payment_actions_query = """
        CREATE TABLE PAYMENT_ACTIONS(
            ID INT AUTO_INCREMENT PRIMARY KEY,
            USER_ID INT,
            SCHEDULE_ID INT,
            ACTION_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            MONEY INT, 
            COACH_ID INT,
            FOREIGN KEY(SCHEDULE_ID) REFERENCES SCHEDULE(ID),
            FOREIGN KEY(USER_ID) REFERENCES USERS(ID),
            FOREIGN KEY(COACH_ID) REFERENCES COACHES(ID)
        );
        """

        do_query(connection, create_train_query)
        do_query(connection, create_users_query)
        do_query(connection, create_actions_query)
        do_query(connection, create_coaches_query)
        do_query(connection, create_payment_actions_query)

except Error as e:
    print(e)