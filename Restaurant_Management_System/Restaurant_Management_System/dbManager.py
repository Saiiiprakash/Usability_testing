from flask_mysqldb import MySQL
import pandas as pd 
from sqlalchemy import create_engine
import mysql.connector
import json

CREATE_TABLE_RESTAURANT = "CREATE TABLE IF NOT EXISTS RESTAURANT (RESTAURANT_ID INT(11) AUTO_INCREMENT PRIMARY KEY, RESTAURANT_NAME VARCHAR(250), ADDRESS VARCHAR(250), PHONE VARCHAR(50))"

CREATE_TABLE_BRANCHES = "CREATE TABLE IF NOT EXISTS BRANCHES (BRANCH_ID INT(11) AUTO_INCREMENT PRIMARY KEY, BRANCH_NAME VARCHAR(250), BRANCH_ADDRESS VARCHAR(250), BRANCH_PHONE VARCHAR(50), RESTAURANT_ID INT(11))"

CREATE_TABLE_STAFF = "CREATE TABLE IF NOT EXISTS STAFF (STAFF_ID INT(11) AUTO_INCREMENT PRIMARY KEY, BRANCH_ID INT(11), NAME VARCHAR(200), PASSWORD VARCHAR(250))"

CREATE_TABLE_INGREDIENT = "CREATE TABLE IF NOT EXISTS INGREDIENT (INGREDIENT_ID INT(11) AUTO_INCREMENT PRIMARY KEY, BRANCH_ID INT(11), FOOD_ID INT(11), INGREDIENT_NAME VARCHAR(250), CALORIES VARCHAR(250))"

CREATE_TABLE_FOOD_ITEM = "CREATE TABLE IF NOT EXISTS FOOD_ITEM (FOOD_ID INT(11) AUTO_INCREMENT PRIMARY KEY,BRANCH_ID INT(11), NAME VARCHAR(250), QUANTITY INT(11), PRICE INT(11))"

CREATE_TABLE_PARKING = "CREATE TABLE IF NOT EXISTS PARKING (PARKING_ID INT(11) AUTO_INCREMENT PRIMARY KEY, BRANCH_ID INT(11))"

CREATE_TABLE_RES_TABLE = "CREATE TABLE IF NOT EXISTS RES_TABLE (TABLE_ID INT(11) AUTO_INCREMENT PRIMARY KEY, BRANCH_ID INT(11))"

CREATE_TABLE_RESERVATION = "CREATE TABLE IF NOT EXISTS RESERVATION (RESERVATION_ID INT(11) AUTO_INCREMENT PRIMARY KEY, TABLE_ID INT(11), DATE_TIME DATE, NO_OF_GUESTS INT(11), PARKING_ID INT(11), BRANCH_ID INT(11), CUSTOMER_ID INT(11), STATUS VARCHAR(200))"


CREATE_TABLE_CUSTOMER_FEEDBACK = "CREATE TABLE IF NOT EXISTS CUSTOMER_FEEDBACK (FEEDBACK_ID INT(11) AUTO_INCREMENT PRIMARY KEY,BRANCH_ID VARCHAR(200), CUSTOMER_RATING INT(2), CUSTOMER_NAME VARCHAR(200))"

CREATE_TABLE_CUSTOMER = "CREATE TABLE IF NOT EXISTS CUSTOMER (CUSTOMER_ID INT(11) AUTO_INCREMENT PRIMARY KEY, CUSTOMER_NAME VARCHAR(250), PASSWORD VARCHAR(250))"


CREATE_TABLE_ORDER = "CREATE TABLE IF NOT EXISTS ORDERS (ORDER_ID INT(11) AUTO_INCREMENT PRIMARY KEY, ORDER_DATE_TIME DATE,FOOD_ID INT(11),  WAIT_TIME INT(11), STATUS VARCHAR(100),TABLE_ID INT(11), BRANCH_ID INT(11),CUSTOMER_ID INT(11))"

def initialize():
    mydb = mysql.connector.connect(host="db",user="user",password="password",database="restaurant")
    cursor = mydb.cursor()
    cursor.execute(CREATE_TABLE_RESTAURANT)
    cursor.execute(CREATE_TABLE_BRANCHES)
    cursor.execute(CREATE_TABLE_STAFF)
    cursor.execute(CREATE_TABLE_INGREDIENT)
    cursor.execute(CREATE_TABLE_FOOD_ITEM)
    cursor.execute(CREATE_TABLE_PARKING)
    cursor.execute(CREATE_TABLE_RES_TABLE)
    cursor.execute(CREATE_TABLE_RESERVATION)
    cursor.execute(CREATE_TABLE_CUSTOMER_FEEDBACK)
    cursor.execute(CREATE_TABLE_CUSTOMER)
    cursor.execute(CREATE_TABLE_ORDER)
    mydb.commit()

def insert_values(data,name):
    data_df =  pd.DataFrame([data])
    
    engine = create_engine("mysql+pymysql://{user}:{pw}@db/{db}"
                       .format(user="user",
                               pw="password",
                               db="restaurant"))
    try:
        data_df.to_sql(name, con = engine, if_exists = 'append', chunksize = 1000,index=False)
    except Exception as e:
        print(name + ": error : "+ str(e))
        raise Exception("Duplicate")
        print("")

def insert_default_values(name):
    restaurants = pd.read_csv(name+".csv")
    
    engine = create_engine("mysql+pymysql://{user}:{pw}@db/{db}"
                       .format(user="user",
                               pw="password",
                               db="restaurant"))
    try:
        restaurants.to_sql(name, con = engine, if_exists = 'append', chunksize = 1000,index=False)
    except Exception as e:
        print(name + ": error : "+ str(e))
        print("")

def list_all_restaurants():
    return fetchAll("SELECT * FROM restaurant")

def list_all_branches_by_restaurant(id):
    return fetchAllParam("SELECT * FROM branches where restaurant_id=%s", (id,))

def list_all_parking_by_branch_id(id):
    return fetchAllParam("SELECT * FROM parking where branch_id=%s and parking_id not in (select parking_id from reservation where status=%s)", (id,"BOOKED",))

def list_all_table_by_branch_id(id):
    return fetchAllParam("SELECT * FROM res_table where branch_id=%s and table_id not in (select table_id from reservation where status=%s)", (id,"BOOKED",))

def list_all_food_by_branch_id(id):
    return fetchAllParam("select * from food_item f inner join ingredient i on i.branch_id = %s and i.branch_id = f.branch_id and i.food_id = f.food_id", (id,))

def validate_staff_login(userid,password):
    jsonData =  fetchAllParam("select * from staff where STAFF_ID=%s and password=%s", (userid,password,))
    return (jsonData)

def list_all_booked_table_by_branch_id(id):
    return fetchAllParam("select * from reservation where branch_id=%s and status=%s", (id,"BOOKED",))

def list_take_away_orders(id,customerId):
    return fetchAllParam("select * from orders o inner join food_item f on o.branch_id=f.branch_id and o.food_id=f.food_id and  o.branch_id=%s and o.customer_id=%s and o.status=%s", (id,customerId,"ORDERED",))

def pay_take_away_orders(branchId,customerId):
    update("update orders set STATUS='PAID' where BRANCH_ID=%s and CUSTOMER_ID=%s",(branchId,customerId,))

def pay_table_orders(tableid,customerId):
    update("update orders set STATUS='PAID' where TABLE_ID=%s and CUSTOMER_ID=%s",(tableid,customerId,))
    update("update reservation set STATUS='CLOSED' where TABLE_ID=%s and CUSTOMER_ID=%s",(tableid,customerId,))


def validate_customer_login(userid,password):
    jsonData =  fetchAllParam("select * from customer where CUSTOMER_ID=%s and password=%s", (userid,password,))
    return (jsonData)
    #print(json.load(jsonData))

def list_all_orders_by_branch_id(id):
    return fetchAllParam("select * from orders o inner join food_item f on o.branch_id=f.branch_id and o.food_id=f.food_id and  o.branch_id=%s ", (id,))

def list_table_orders(id,tableId):
    return fetchAllParam("select * from orders o inner join food_item f on o.branch_id=f.branch_id and o.food_id=f.food_id and  o.branch_id=%s and o.table_id=%s and o.status=%s", (id,tableId,"ORDERED",))

def list_orders_by_tableId(tableId):
    return fetchAllParam("select * from orders o inner join food_item f on o.branch_id=f.branch_id and o.food_id=f.food_id and  o.table_id=%s and o.status=%s", (tableId,"ORDERED",))

def list_table_reservation(customerId):
    return fetchAllParam("select * from reservation where customer_id=%s and status=%s", (customerId,"BOOKED",))


def list_feedback(branchId):
    return fetchAllParam("select * from customer_feedback where branch_id=%s ", (branchId,))

def list_branch_for_feedback(id):
    return fetchAllParam("SELECT * FROM branches b inner join restaurant r on b.RESTAURANT_ID=r.RESTAURANT_ID and b.branch_id in (select distinct(branch_id) from orders where customer_id=%s) ", (id,))

def update(query, param):
    mydb = mysql.connector.connect(host="db",user="user",password="password",database="restaurant")
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(query,param)
    mydb.commit()

def fetchAllParam(query, param):
    mydb = mysql.connector.connect(host="db",user="user",password="password",database="restaurant")
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(query,param)
    myresult = cursor.fetchall()
    return myresult

def fetchAll(query):
    mydb = mysql.connector.connect(host="db",user="user",password="password",database="restaurant")
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(query)
    myresult = cursor.fetchall()
    return myresult
    