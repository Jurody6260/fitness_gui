from mysql.connector import connect, Error
import time

DB_USER = "root"
DB_PSWD = "root"
DB_NAME = "fitness"

def getConnection():
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database="rfid",
        ) as connection:
            
            return connection
    except Error as e:
        print(e)
        return None
def saveUser(user_id,RFID,NAME,TEL_NUMBER,SCHEDULE_ID,START_DATE,END_DATE,TRAIN_AMOUNT,USER_LEVEL):
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
            #read_schedule="""SELECT ID FROM SCHEDULE WHERE NAME=%s """
           # cursor.execute(read_schedule,(schedule,))
           # record = cursor.fetchone()
           # if record:
               # SCHEDULE_ID = record[0]
            read_user="SELECT ID FROM USERS WHERE ID = "+user_id
            cursor.execute(read_user)
            record = cursor.fetchone()
            if not record:
                print ("insert query")
                insert_user_query = """
                    INSERT INTO USERS(RFID, NAME, TEL_NUMBER,SCHEDULE_ID,START_DATE,END_DATE,TRAIN_AMOUNT,USER_LEVEL) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                insert_blob_tuple = (RFID, NAME, TEL_NUMBER,SCHEDULE_ID,START_DATE,END_DATE,TRAIN_AMOUNT,USER_LEVEL)
                
                result = cursor.execute(insert_user_query, insert_blob_tuple)
                    
            elif id>-1:
                print ("update query")
                insert_user_query = """
                    UPDATE USERS SET RFID=%s,NAME=%s,TEL_NUMBER=%s, SCHEDULE_ID=%s,START_DATE=%s, END_DATE=%s, TRAIN_AMOUNT=%s, USER_LEVEL=%s WHERE ID=%s
                    """
                insert_blob_tuple = (RFID, NAME,TEL_NUMBER, SCHEDULE_ID,START_DATE,END_DATE,TRAIN_AMOUNT,USER_LEVEL,user_id)
                
                result = cursor.execute(insert_user_query, insert_blob_tuple)
            connection.commit()
            
    except Exception as e:
        print("saveUser:",e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
def saveCoach(user_id,NAME):
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
            #read_schedule="""SELECT ID FROM SCHEDULE WHERE NAME=%s """
           # cursor.execute(read_schedule,(schedule,))
           # record = cursor.fetchone()
           # if record:
               # SCHEDULE_ID = record[0]
            read_user="SELECT ID FROM COACHES WHERE ID = "+user_id
            cursor.execute(read_user)
            record = cursor.fetchone()
            if not record:
                print ("insert query")
                insert_user_query = "INSERT INTO COACHES(NAME) VALUES ('"+NAME+"')" 
              #  print (insert_user_query) 
                result = cursor.execute(insert_user_query)
                    
            elif id>-1:
                print ("update query")
                insert_user_query = """
                    UPDATE COACHES SET NAME=%s WHERE ID=%s
                    """
                insert_blob_tuple = (NAME,user_id)
                
                result = cursor.execute(insert_user_query, insert_blob_tuple)
            connection.commit()
            
    except Exception as e:
        print("saveCoach:",e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()            
def saveSchedule(id,NAME,START_TIME,END_TIME,TRAIN_AMOUNT):
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
            
            read_user="""SELECT ID FROM SCHEDULE WHERE ID=%s """
            cursor.execute(read_user,(id,))
            record = cursor.fetchone()
            if not record:
                print ("insert query")
                insert_user_query = """
                INSERT INTO SCHEDULE(NAME,START_TIME,END_TIME,TRAIN_AMOUNT) VALUES (%s,%s,%s,%s)
                """
                insert_blob_tuple = (NAME, START_TIME,END_TIME,TRAIN_AMOUNT)
                
                result = cursor.execute(insert_user_query, insert_blob_tuple)
                    
            elif id>-1:
                print ("update query")
                insert_user_query = """
                UPDATE SCHEDULE SET NAME=%s, START_TIME=%s,END_TIME=%s, TRAIN_AMOUNT=%s WHERE ID=%s
                    """
                insert_blob_tuple = (NAME, START_TIME,END_TIME,TRAIN_AMOUNT,id)
                
                result = cursor.execute(insert_user_query, insert_blob_tuple)
            connection.commit()
       
    except Exception as e:
        print("findUser:",e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()

def getSchedule(with_new=1):
    schedule_names=[]
    schedule_ids=[]
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
            read_group_query="""SELECT ID, NAME FROM SCHEDULE """
            cursor.execute(read_group_query,())
            record = cursor.fetchall()
            for row in record:
                schedule_names.append(row[1])
                schedule_ids.append(row[0])
            if with_new==1:
                schedule_names.append("new schedule")
                schedule_ids.append(-1)
            connection.commit() 
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return schedule_ids, schedule_names

def getUsersByScheduleID(SCHEDULE_ID):
    user_names=[]
    user_ids=[]
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
            read_group_query="""SELECT ID, NAME FROM USERS WHERE SCHEDULE_ID=%s order by name asc"""
            cursor.execute(read_group_query,(SCHEDULE_ID,))
            record = cursor.fetchall()
            for row in record:
                user_names.append(row[1])
                user_ids.append(row[0])
            user_names.append("new USER")
            user_ids.append(-1)
            connection.commit() 
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return user_ids, user_names
def getCoaches():
    coach_names=[]
    coach_ids=[]
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
            read_group_query="""SELECT ID, NAME FROM COACHES order by name asc"""
            cursor.execute(read_group_query,())
            record = cursor.fetchall()
            for row in record:
                coach_names.append(row[1])
                coach_ids.append(row[0])
            coach_names.append("new Coach")
            coach_ids.append(-1)
            connection.commit() 
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return coach_ids, coach_names

def getCouchByID(couch_id):
    ID=-1
    NAME="new schedule"
   
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
            read_group_query="""SELECT ID, NAME FROM COACHES where ID = %s"""
            cursor.execute(read_group_query,(couch_id,))
            row = cursor.fetchone()
            if row:
                ID=row[0]
                NAME=row[1]
                
            
            connection.commit() 
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return ID, NAME
def getScheduleByID(schedule_id):
    ID=-1
    NAME="new schedule"
    START_TIME="8:30:00"
    END_TIME="11:35:00"
    TRAIN_AMOUNT=12
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
            read_group_query="""SELECT ID, NAME,START_TIME, END_TIME,TRAIN_AMOUNT FROM SCHEDULE where ID = %s"""
            cursor.execute(read_group_query,(schedule_id,))
            row = cursor.fetchone()
            if row:
                ID=row[0]
                NAME=row[1]
                START_TIME=row[2]
                END_TIME=row[3]
                TRAIN_AMOUNT=row[4]
            
            connection.commit() 
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return ID, NAME,START_TIME,END_TIME,TRAIN_AMOUNT
def getUserByID(user_id):
    ID=-1
    RFID="000"
    NAME="new user"
    TEL_NUMBER="+998XXXXXXXXX"
    SCHEDULE_ID=0
    START_DATE="2021.01.01"
    END_DATE="2021.02.01"
    TRAIN_AMOUNT=0
    REGISTERED_DATE="2021.01.01"
    USER_LEVEL=0
    
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
            read_group_query="""SELECT ID, RFID,NAME,TEL_NUMBER,SCHEDULE_ID,START_DATE,END_DATE,TRAIN_AMOUNT,DATE(REGISTERED_DATE) AS REGISTERED_DATE ,USER_LEVEL FROM USERS where ID = %s"""
            cursor.execute(read_group_query,(user_id,))
            row = cursor.fetchone()
            if row:
                ID=row[0]
                RFID=row[1]
                NAME=row[2]
                TEL_NUMBER=row[3]
                SCHEDULE_ID=row[4]
                START_DATE=row[5]
                END_DATE=row[6]
                TRAIN_AMOUNT=row[7]
                REGISTERED_DATE=row[8]
                USER_LEVEL=row[9]
                read_group_query="""SELECT NAME FROM SCHEDULE where ID = %s"""
                cursor.execute(read_group_query,(SCHEDULE_ID,))
                row = cursor.fetchone()
                SCHEDULE_ID=row[0]
            connection.commit() 
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return ID, RFID,NAME,TEL_NUMBER,SCHEDULE_ID,START_DATE,END_DATE,TRAIN_AMOUNT,REGISTERED_DATE,USER_LEVEL

def do_query(query):
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()
           # print(query)
            cursor.execute(query)         
            connection.commit() 
    except Exception as e:
        print("do_query:",e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()

            
import datetime
def findUser(RFID,ACTION_TYPE):
    name = None
    user_id =None
    USER_LEVEL=None
    SCHEDULE_NAME=None
    TRAIN_AMOUNT=0
    permission=0
   # gender=None
    
    try:
        with connect(
            host="localhost",
            user=DB_USER,
            password=DB_PSWD,
            database=DB_NAME,
        ) as connection:
            cursor = connection.cursor()       

            read_user_query="""SELECT USERS.ID,USERS.NAME,USERS.TRAIN_AMOUNT,USERS.SCHEDULE_ID,USERS.USER_LEVEL,USERS.END_DATE,USERS.START_DATE,SCHEDULE.NAME  FROM (USERS JOIN SCHEDULE ON USERS.SCHEDULE_ID=SCHEDULE.ID) WHERE RFID=%s limit 1"""
            cursor.execute(read_user_query,(RFID,))
            record = cursor.fetchone()
            
            if record:
                user_id = record[0]
                name = record[1]
                TRAIN_AMOUNT=record[2]
                SCHEDULE_ID=record[3]
                USER_LEVEL=record[4]
                END_DATE=record[5]
                START_DATE=record[6]
                SCHEDULE_NAME=record[7]
                #print(record)
                read_user_query="SELECT ID,START_TIME,END_TIME FROM SCHEDULE WHERE ID=%s and START_TIME<=NOW() and END_TIME>=NOW()"
                cursor.execute(read_user_query,(SCHEDULE_ID,))
                today_=time.strftime("%Y.%m.%d")
                record = cursor.fetchone()
                if record and TRAIN_AMOUNT>0 and START_DATE<=datetime.date.today() and END_DATE>=datetime.date.today(): 
                    permission=1
                    START_TIME=record[1]
                    END_TIME=record[2]
                
                    read_actions_query="SELECT * FROM ACTIONS WHERE USER_ID=%s and %s %s<=ACTION_DATE and %s %s>=ACTION_DATE limit 1 "
                    cursor.execute(read_actions_query,(user_id,today_,START_TIME,today_,END_TIME))
                    record = cursor.fetchone()
                    #print (record)
                    if not record:
                        
                        insert_user_query = """
                        UPDATE USERS SET TRAIN_AMOUNT=%s WHERE ID=%s
                        """
                        insert_blob_tuple = (TRAIN_AMOUNT-1,user_id)
                
                        result = cursor.execute(insert_user_query, insert_blob_tuple) 
                    insert_action_query = """
                    INSERT INTO ACTIONS(USER_ID,ACTION_TYPE) VALUES (%s,%s);
                    """
                    insert_blob_tuple = (user_id, ACTION_TYPE)
                    result = cursor.execute(insert_action_query, insert_blob_tuple)   
                elif USER_LEVEL>9:
                    permission=1
                    insert_action_query = """
                    INSERT INTO ACTIONS(USER_ID,ACTION_TYPE) VALUES (%s,%s);
                    """
                    insert_blob_tuple = (user_id, ACTION_TYPE)
                    result = cursor.execute(insert_action_query, insert_blob_tuple)
                   # print (record)
               # picture = record[2]
               # group_id = record[3]
               # is_guest=record[4]
               # gender=record[5]
            #if not user_id ==None:
               # read_group_query="""SELECT NAME FROM GROUPS WHERE ID=%s"""
               # cursor.execute(read_group_query, (group_id,))
               # record = cursor.fetchone()
                #group_id = record[0]
            
               # if is_guest==0:
                


                connection.commit() 
    except Exception as e:
        print("findUser:",e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    
    return user_id,name,USER_LEVEL,SCHEDULE_NAME,TRAIN_AMOUNT,permission
def create_new_group(name):
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            cursor = connection.cursor()
            insert_action_query ="INSERT INTO GROUPS(NAME) VALUES ('"+name+"');" 
            #insert_blob_tuple = (name)
            result = cursor.execute(insert_action_query)
            connection.commit()
            print (cursor.lastrowid)
    except Exception as e:
        print(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def getAction():
    id=None
    user_id=None
    action_type=None
    action_date=None
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            cursor = connection.cursor()
            read_user_query="""SELECT ID,USER_ID,ACTION_TYPE,ACTION_DATE FROM ACTIONS WHERE IS_SEND=0 LIMIT 1"""
            cursor.execute(read_user_query)
            record = cursor.fetchone()
            if record:
                id = record[0]
                user_id=record[1]
                action_type=record[2]
                action_date=record[3]
            connection.commit() 
    except Exception as e:
        print("getAction:",e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return id, user_id, action_type, action_date
            

def getUserById(user_id_global):
    name = None
    picture = None
    user_id =None
    group_id=None
    RFID=None
    is_guest=0
    gender=0
    
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            cursor = connection.cursor()
            read_user_query="""SELECT ID,NAME,RFID,IMG,GROUP_ID,IS_GUEST,GENDER FROM USERS WHERE ID=%s LIMIT 1"""
            cursor.execute(read_user_query, (user_id_global,))
            record = cursor.fetchone()
            user_id = record[0]
            name = record[1]
            RFID= record[2]
            picture = record[3]
            group_id = record[4]   
            is_guest = record[5]  
            gender = record[6]  
           # print record   
            connection.commit() 
    except Exception as e:
        print("getUserById:",e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    
    return user_id,name, RFID,picture,group_id,is_guest,gender

def getActionForMonth(user_id,year,month,days):
    in_hours=[None]*days
    out_hours=[None]*days
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            cursor = connection.cursor()
           # readTable()
            if month<10:
                month_str="0"+str(month)
            else:
                month_str=str(month)
            year=str(year)
            for i in range(1,days):
                
                if i<10:
                    days_str="0"+str(i)
                else:
                    days_str=str(i)
                date=year+"-"+month_str+"-"+days_str
                #print date
                read_group_query="SELECT DATE_FORMAT(ACTION_DATE, '%H:%i:%S')myDate FROM ACTIONS WHERE USER_ID="+str(user_id)+" AND ACTION_TYPE=1 AND ACTION_DATE BETWEEN '"+date+" 00:00:00' and '"+date+" 23:00:00' ORDER BY ID asc LIMIT 1;"#+str(year)+"-0"+str(month)+"-00 00:00:00' and '"+str(year)+"-0"+str(month)+"-"+str(days)+" 23:59:59' ORDER BY ID asc LIMIT 1;"
                cursor.execute(read_group_query)
                record = cursor.fetchone()
               # print read_group_query
                if not record == None:
                    in_hours[i-1]=record[0]
                   # print str(in_hours[i-1])
                
                   

                read_group_query="SELECT DATE_FORMAT(ACTION_DATE, '%H:%i:%S')myDate FROM ACTIONS WHERE USER_ID="+str(user_id)+" AND ACTION_TYPE=2 AND ACTION_DATE BETWEEN '"+date+" 00:00:00' and '"+date+" 23:59:59' ORDER BY ID desc LIMIT 1;"
                cursor.execute(read_group_query)
                record = cursor.fetchone()
                if not record == None:
                    out_hours[i-1]=record[0]
            
            connection.commit() 
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return in_hours,out_hours
def getUsersByGroup(group_id):
    user_names=[]
    user_ids=[]
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            cursor = connection.cursor()
            read_group_query="""SELECT ID,NAME FROM USERS WHERE GROUP_ID=%s """
            cursor.execute(read_group_query,(group_id,))
            record = cursor.fetchall()
            for row in record:
                user_names.append(row[1])
                user_ids.append(row[0])
            user_names.append("new user")
            user_ids.append(-1)
            connection.commit() 
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return user_ids,user_names
def getAllUsersCount():
    all_std=0
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            cursor = connection.cursor()
            read_group_query="""SELECT COUNT(*) FROM USERS WHERE IS_GUEST=0"""
            cursor.execute(read_group_query)
            record = cursor.fetchone()
            all_std=int(record[0])
           # print ("all_std:",all_std)
            
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return all_std

def getGroups():
    group_names=[]
    group_ids=[]
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            cursor = connection.cursor()
            read_group_query="""SELECT ID,NAME FROM GROUPS """
            cursor.execute(read_group_query)
            record = cursor.fetchall()
            for row in record:
                group_names.append(row[1])
                group_ids.append(row[0])
            connection.commit() 
    except Exception as e:
        print(e)
    finally:    
        if connection.is_connected():
            cursor.close()
            connection.close()
    return group_ids,group_names
from datetime import date
def getStatistics():
    all_users=0
    registered=0
   
    today = date.today()
    sql_date=today.strftime("%d/%m/%Y")
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            get_query = """
                SELECT COUNT(DISTINCT USER_ID) FROM ACTIONS WHERE DATE(`ACTION_DATE`) = CURDATE()"""
            cursor = connection.cursor()
            cursor.execute(get_query)
            record = cursor.fetchone()
            registered=record[0]
    except Exception as e:
        print(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return registered
def insertUser(user_id,RFID,NAME,GROUP_ID,photo,user_is_guest,user_gender):
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            cursor = connection.cursor()
            read_user="""SELECT ID FROM USERS WHERE ID=%s """
            cursor.execute(read_user,(user_id,))
            record = cursor.fetchone()
            if not record:
               # print ("insert query")
                insert_user_query = """
                INSERT INTO USERS(ID,RFID, NAME, GROUP_NAME,IS_GUEST,GENDER) VALUES (%s,%s,%s,%s,%s,%s)
                """
                insert_blob_tuple = (user_id,RFID, NAME, GROUP_ID,user_is_guest,user_gender)
                
                result = cursor.execute(insert_user_query, insert_blob_tuple)
                connection.commit()
            else:
               # print ("update query")
                insert_user_query = """
                UPDATE USERS SET RFID=%s,NAME=%s, GROUP_NAME=%s,IS_GUEST=%s, GENDER=%s WHERE ID=%s
                """
                insert_blob_tuple = (RFID, NAME, GROUP_ID,user_is_guest,user_gender,user_id)
                
                result = cursor.execute(insert_user_query, insert_blob_tuple)
                connection.commit()
    except Exception as e:
        print(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def insertAction(USER_ID,ACTION_TYPE):
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            cursor = connection.cursor()
            insert_action_query = """
            INSERT INTO ACTIONS(USER_ID,ACTION_TYPE) VALUES (%s,%s);
            """
            insert_blob_tuple = (USER_ID, ACTION_TYPE)
            result = cursor.execute(insert_action_query, insert_blob_tuple)
            connection.commit()
    except Error as e:
        print(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def readTable():
    try:
        with connect(
            host="localhost",
            user="pi",
            password="raspberry",
            database="rfid",
        ) as connection:
            select_groups_query = "SELECT * FROM ACTIONS"
            with connection.cursor() as cursor:
                cursor.execute(select_groups_query)
                result = cursor.fetchall()
                for row in result:
                    print(row)
    except Error as e:
        print(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


