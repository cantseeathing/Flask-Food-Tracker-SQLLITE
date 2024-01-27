from flask import Flask, render_template, url_for, g, request, redirect
from dotenv import load_dotenv
import sqlite3
import os
import helper as helper

load_dotenv(verbose=True)

app = Flask(__name__)

DATABASE = os.getenv('DB')


def get_db():
    """
    Opens a new database connection if there is none
    :return: database connection instance
    """
    # # CHECK IF THE DB INSTANCE EXIST OR NOT
    db = getattr(g, '_database', None)
    if db is None:
        # # CONNECT TO THE DB
        db = g._database = sqlite3.connect(DATABASE)
        # # GET BACK THE DATA FROM THE DB IN ROW FORMAT
        db.row_factory = sqlite3.Row
        # # CREATE THE DB IF IT DOES NOT EXIST
        helper.create_tables(db=db)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET'])
def home():
    # # GET THE DB INSTANCE
    db = get_db()
    # # QUERY ALL THE DAYS FROM THE INTAKE TABLE IN THE DB
    all_days = helper.query_all_days(db=db)
    print([dict(x) for x in helper.query_all_foods(db=db)])
    print(all_days)
    days_list = []
    print('here')
    # # IF THE DB RETURN INTAKE DATES
    if len(all_days) != 0:
        # # CONVERT THE DATA TO A LIST OF DICTIONARIES
        for days in all_days:
            print('days: ', days)
            days = dict(days)
            aggregate = helper.aggregate_values(db=db, result=[days])
            days.update(aggregate)
            days_list.append(days)
        print(days_list)
    return render_template('home.html',
                           title='Food Tracker App',
                           days_list=days_list)


@app.route('/food_catalogue', methods=['GET'])
def food_catalogue():
    """
    View all food in the FOODS table and edit any entry
    """
    db = get_db()
    foods = helper.query_all_foods(db=db)
    return render_template('food_catalogue.html',
                           title='Add Food',
                           foods=foods)




@app.route('/add_food', methods=['GET', 'POST'])
def add_food():
    """
    Add food to the food table in the database
    """
    # # GET DB INSTANCE
    db = get_db()
    # # POST REQUEST
    if request.method == 'POST':
        # # CHECK IF THE FORM RETURNS FOOD ID FIELD THEN THE USER WANTS TO EDIT FOOD VALUES
        if request.form.get('food_id') is not None:
            print(request.form.get('food_id'))
        # # NO FOOD ID FIELD
        else:
            # # GET THE FOOD NAME, PROTEIN, CARBS, AND FAT VALUE FROM THE FORM
            food_name = request.form.get('food_name', type=str, default='Unnamed Food')
            food_protein = request.form.get('food_protein', type=int, default=0)
            food_carbs = request.form.get('food_carbs', type=int, default=0)
            food_fat = request.form.get('food_fat', type=int, default=0)
            food_cals = request.form.get('food_cal', type=int, default=0)
            # # INSERT THE FOOD TO THE FOODS TABLE
            helper.insert_food(food_name, food_protein, food_carbs, food_fat, food_cals, db=db)
        # # RETURN THE USER TO THE FOOD CATALOGUE PAGE
        return redirect(url_for('food_catalogue'))
    return render_template('add_food.html',
                           title='Add Food')


@app.route('/add_day', methods=['GET', 'POST'])
def add_day():
    db = get_db()
    if request.method == 'POST':
        # # REMOVE FOOD FROM A DATE INTAKE
        if request.form.get('food_id') is not None:
            date = request.form.get('date', type=str)
            food_id = request.form.get('food_id', type=int)
            print('here', date, food_id)
            helper.delete_food(db=db, id=food_id, date=date)
            return redirect(url_for('add_day', date=date))
        # # ADD FOOD TO A DATE INTAKE
        food_id = request.form.get('food', type=str)
        date = request.form.get('date', type=str)
        helper.insert_intake(db=db, food_id=food_id, date=date)
        print(food_id, date)
        return redirect(url_for('add_day', date=date))
    date = request.args.get('date', type=str, default=None)
    # # NO DATE WAS PROVIDED BY THE USER
    if date is None or date == '':
        # # REDIRECT THE USER BACK TO THE HOME PAGE
        return redirect(url_for('home'))
    # # QUERY THE DB FOR THE PROVIDED DATE
    result = helper.query_db_date(db=db, date=date)
    # print("date: ", date, " intake", dict(result[0]))
    # # QUERY THE DB FOR ALL THE AVAILABLE FOODS
    foods = helper.query_all_foods(db=db)
    print("all foods: ", foods)
    print("date result: ", helper.convert_result_to_dict(result))
    aggregate = helper.aggregate_values(db=db, result=result)
    print(aggregate)
    return render_template('add_day.html',
                           title='Add Day',
                           date=date,
                           foods=foods,
                           result=result,
                           aggregate=aggregate)


if __name__ == "__main__":
    app.run()
