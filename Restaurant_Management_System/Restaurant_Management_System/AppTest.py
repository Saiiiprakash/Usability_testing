from dbManager import list_all_restaurants,list_all_branches_by_restaurant,list_all_parking_by_branch_id,list_all_table_by_branch_id,list_all_food_by_branch_id,validate_staff_login,validate_customer_login
import pandas as pd

def runTestSuite():
    test_list_restaurants()
    test_list_branches_by_restaurant_id()
    test_list_parking_by_branch_id()
    test_list_table_by_branch_id()
    test_list_all_food_by_branch_id()
    test_validate_staff_login()
    test_validate_customer_login()

def test_list_restaurants():
    print(list_all_restaurants())
    
def test_list_branches_by_restaurant_id():
    print(list_all_branches_by_restaurant(1))
    
def test_list_parking_by_branch_id():
    print(list_all_parking_by_branch_id(1))

def test_list_table_by_branch_id():
    print(list_all_table_by_branch_id(1))

def test_list_all_food_by_branch_id():
    print(list_all_food_by_branch_id(1))

def test_validate_staff_login():
    print(validate_staff_login(1,"john"))

def test_validate_customer_login():
    print(validate_customer_login(1,"john"))
    

#runTestSuite()