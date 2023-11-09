import random
from flask import render_template, request, session, redirect, url_for, flash
from flask import Flask
from datetime import datetime
import re
import os
from dbManager import initialize, insert_default_values, validate_customer_login, validate_staff_login, insert_values, list_all_restaurants, list_all_branches_by_restaurant, list_all_food_by_branch_id, list_all_parking_by_branch_id, list_all_table_by_branch_id,list_all_booked_table_by_branch_id,list_take_away_orders,pay_take_away_orders,list_all_orders_by_branch_id,list_table_orders,list_orders_by_tableId,list_table_reservation,pay_table_orders,list_feedback,list_branch_for_feedback
from flask_mysqldb import MySQL
import mysql.connector
from AppTest import runTestSuite

app = Flask(__name__,  template_folder='templates', static_folder='static')
app.secret_key = 'S3c48kee39djjh8@!'
app.config['MYSQL_HOST'] = 'db'
app.config["MYSQL_USER"] = "user"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "restaurant"
app.config["MYSQL_PORT"] = 3306
mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST' and (len(validate_customer_login(request.form['user_id'], request.form['password'])) > 0):
        session["user_name"] = validate_customer_login(request.form['user_id'], request.form['password'])[0]["CUSTOMER_NAME"]
        session["user_id"] = request.form['user_id']
        return redirect(url_for('customer_home'))
    elif request.method == 'POST' and (len(validate_staff_login(request.form['user_id'], request.form['password'])) > 0):
        session["user_id"] = request.form['user_id']
        session["BRANCH_ID"] = validate_staff_login(request.form['user_id'], request.form['password'])[0]["BRANCH_ID"]
        return redirect(url_for('staff_home'))
    else:
        flash('Invalid login')
    return render_template("login.html")


@app.route('/customer_home', methods=['GET'])
def customer_home():
    return render_template("customer_home.html")

@app.route('/feedback', methods=['GET','POST'])
def feedback():
    if "rating" in request.form and request.form!="":
        insert_values({
            "BRANCH_ID":request.form["branch_id"],
            "CUSTOMER_RATING":request.form["rating"],
            "CUSTOMER_NAME":session["user_name"],
            },"CUSTOMER_FEEDBACK")
        flash("Rating Submitted successfully")
        return render_template("customer_home.html")
    else:
        return render_template("feedback.html", branches=list_branch_for_feedback(session["user_id"]))

@app.route('/customer_menu', methods=['GET', 'POST'])
def customer_menu():
    if "restaurant" in request.form and "branch" in request.form:
        return render_template("customer_menu.html", restaurants=list_all_restaurants(), selected_restaurant=int(request.form["restaurant"]),selected_branch=int(request.form["branch"]), branches=list_all_branches_by_restaurant(request.form["restaurant"]), food_items=list_all_food_by_branch_id(request.form["branch"]))
    elif "restaurant" in request.form:
        return render_template("customer_menu.html", restaurants=list_all_restaurants(), selected_restaurant=int(request.form["restaurant"]), selected_branch=list_all_branches_by_restaurant(request.form["restaurant"])[0]["BRANCH_ID"], branches=list_all_branches_by_restaurant(request.form["restaurant"]))
    else:
        return render_template("customer_menu.html", restaurants=list_all_restaurants())
    
@app.route('/take_away', methods=['GET', 'POST'])
def take_away():
    if "branchid" in request.form and "foodId"  in request.form :
        insert_values({
            "ORDER_DATE_TIME": datetime.now(),
            "FOOD_ID":request.form["foodId"],
            "WAIT_TIME":random.randrange(5, 40),
            "STATUS":"ORDERED",
            "BRANCH_ID":request.form["branchid"],
            "CUSTOMER_ID":session["user_id"]
        },"orders")
        return render_template("take_away.html", restaurants=list_all_restaurants(), selected_restaurant=int(request.form["restaurantId"]),selected_branch=int(request.form["branchid"]), branches=list_all_branches_by_restaurant(request.form["restaurantId"]), food_items=list_all_food_by_branch_id(request.form["branchid"]), orders=list_take_away_orders(request.form["branchid"], session['user_id']))
    if "restaurant" in request.form and "branch" in request.form:
        return render_template("take_away.html", restaurants=list_all_restaurants(), selected_restaurant=int(request.form["restaurant"]),selected_branch=int(request.form["branch"]), branches=list_all_branches_by_restaurant(request.form["restaurant"]), food_items=list_all_food_by_branch_id(request.form["branch"]), orders=list_take_away_orders(request.form["branch"], session['user_id']))
    elif "restaurant" in request.form:
        return render_template("take_away.html", restaurants=list_all_restaurants(), selected_restaurant=int(request.form["restaurant"]), selected_branch=list_all_branches_by_restaurant(request.form["restaurant"])[0]["BRANCH_ID"], branches=list_all_branches_by_restaurant(request.form["restaurant"]))
    else:
        return render_template("take_away.html", restaurants=list_all_restaurants())

@app.route('/take_away_payment', methods=['GET', 'POST'])
def take_away_payment():
    return render_template("take_away_payment.html", selected_branch=int(request.form["branchid"]),
                           orders=list_take_away_orders(request.form["branchid"], session['user_id']))

@app.route('/take_away_pay', methods=['GET', 'POST'])
def take_away_pay():
    pay_take_away_orders(request.form['branchid'],session["user_id"])
    flash("Payment made successfully")
    return render_template("customer_home.html")

@app.route('/make_table_pay', methods=['GET', 'POST'])
def make_table_pay():
    pay_table_orders(request.form['tableid'],session["user_id"])
    flash("Payment made successfully")
    return render_template("customer_home.html")


@app.route('/take_orders', methods=['GET', 'POST'])
def take_orders():
    branchId = session["BRANCH_ID"]
    if "tableId" in request.form and "foodId" in request.form :
        insert_values({
            "ORDER_DATE_TIME": datetime.now(),
            "FOOD_ID":request.form["foodId"],
            "WAIT_TIME":random.randrange(5, 40),
            "STATUS":"ORDERED",
            "BRANCH_ID":branchId,
            "TABLE_ID":request.form["tableId"],
            "CUSTOMER_ID":request.form["customerId"]
        },"orders")
        return render_template("take_orders.html", tables = list_all_booked_table_by_branch_id(branchId), selected_table=int(request.form["tableId"]) ,food_items=list_all_food_by_branch_id(branchId), customerId=list_all_booked_table_by_branch_id(branchId)[0]["CUSTOMER_ID"], orders=list_table_orders(branchId,request.form["tableId"]))
    if "table" in request.form and request.form["table"]!="":
        return render_template("take_orders.html", tables = list_all_booked_table_by_branch_id(branchId), selected_table=int(request.form["table"]) ,food_items=list_all_food_by_branch_id(branchId), customerId=list_all_booked_table_by_branch_id(branchId)[0]["CUSTOMER_ID"], orders=list_table_orders(branchId,request.form["table"]))
    else:
        return render_template("take_orders.html", tables = list_all_booked_table_by_branch_id(branchId))
 

@app.route('/book_table', methods=['GET', 'POST'])
def book_table():
    if "restaurant" in request.form and "branch" in request.form and "parking" in request.form and "table" in request.form and "noofpersons" in request.form and request.form["noofpersons"]!="" and request.form["table"]!="" and request.form["parking"]!="":
        flash('Table booked successfully')
        insert_values({
            "TABLE_ID": request.form["table"],
            "PARKING_ID": request.form["parking"],
            "NO_OF_GUESTS": request.form["noofpersons"],
            "BRANCH_ID": request.form["branch"],
            "CUSTOMER_ID": session["user_id"],
            "DATE_TIME":datetime.now(),
            "STATUS":"BOOKED"
        }, "RESERVATION")
        return render_template("customer_home.html")
    elif "restaurant" in request.form and "branch" in request.form:
        return render_template("book_table.html", restaurants=list_all_restaurants(), selected_restaurant=int(request.form["restaurant"]), branches=list_all_branches_by_restaurant(request.form["restaurant"]), parkings=list_all_parking_by_branch_id(request.form["branch"]), tables=list_all_table_by_branch_id(request.form["branch"]),selected_branch=int(request.form["branch"]))
    elif "restaurant" in request.form:
        return render_template("book_table.html", restaurants=list_all_restaurants(), selected_restaurant=int(request.form["restaurant"]), branches=list_all_branches_by_restaurant(request.form["restaurant"]))
    else:
        return render_template("book_table.html", restaurants=list_all_restaurants())


@app.route('/make_payment', methods=['GET',"POST"])
def make_payment():
    if "table" in request.form  and request.form["table"]!="":
        return render_template("make_payment.html", selected_table=int(request.form["table"]),orders=list_orders_by_tableId(request.form["table"]),tables=list_table_reservation(session["user_id"]))
    else:
        return render_template("make_payment.html",tables=list_table_reservation(session["user_id"]))

@app.route('/staff_home', methods=['GET'])
def staff_home():
    return render_template("staff_home.html")

@app.route('/order_history', methods=['GET'])
def order_history():
    return render_template("order_history.html", orders=list_all_orders_by_branch_id(session['BRANCH_ID']))


@app.route('/feedback_history', methods=['GET'])
def feedback_history():
    return render_template("feedback_history.html", orders=list_feedback(session['BRANCH_ID']))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if (request.form["user_id"] != "" and request.form["user_name"] != "" and request.form["password"] != ""):
            try:
                insert_values(
                    {"customer_id": request.form["user_id"], "customer_name": request.form["user_name"], "password": request.form["password"]}, "CUSTOMER")
                flash('Successfully signed up')
            except:
                flash("UserId already Used or taken")
        else:
            flash('Invalid Details. Please fill again')
    return render_template("signup.html")


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Successfully Logged Out')
    return redirect(url_for('login'))


if __name__ == "__main__":
    print("initialize")
    initialize()
    files = ["restaurant", "branches", "staff",
             "ingredient", "food_item", "parking", "res_table"]
    for key in files:
        insert_default_values(key)
    try:
        runTestSuite()
    except:
        print("")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
