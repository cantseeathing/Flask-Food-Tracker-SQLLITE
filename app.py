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
    all_days = helper.get_all_dates(db=db)
    all_days = helper.convert_result_to_dict(all_days)
    days_data = []
    # # IF THE DB RETURN INTAKE DATES
    if len(all_days) != 0:
        # # CONVERT THE DATA TO A LIST OF DICTIONARIES
        for day in all_days:
            temp = dict()
            temp['date'] = day.get('date')
            temp['count'] = 0
            temp['protein'] = 0
            temp['calories'] = 0
            temp['carbohydrates'] = 0
            temp['fats'] = 0
            foods_in_date = [x.get('food_id') for x in helper.convert_result_to_dict(helper.query_db_date(db=db, date=temp['date']))]
            for food_id in foods_in_date:
                food = dict(helper.query_food(db=db, food_id=food_id))
                temp['count'] += 1
                temp['protein'] += food['protein']
                temp['calories'] += food['calories']
                temp['carbohydrates'] += food['carbohydrates']
                temp['fats'] += food['fat']
            days_data.append(temp)
    return render_template('home.html',
                           title='Food Tracker App',
                           days_data=days_data)


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


@app.route('/edit_food', methods=['GET'], defaults={'food_id': None})
@app.route('/edit_food/', methods=['GET'], defaults={'food_id': None})
@app.route('/edit_food/<int:food_id>', methods=['GET', 'POST'])
def edit_food(food_id: int):
    """
    Edit an existing food item in the FOODS table
    """
    # # GET DB INSTANCE
    db = get_db()
    # # IF NO FOOD ID IS PASSED THEN TAKE THE USER BACK TO THE FOOD CATALOGUE
    if food_id is None:
        return redirect(url_for('food_catalogue'))
    # # POST REQUEST
    if request.method == 'POST':
        # # GET THE FOOD NAME, PROTEIN, CARBS, AND FAT VALUE FROM THE FORM
        food_name = request.form.get('food_name', type=str, default='Unnamed Food')
        food_protein = request.form.get('food_protein', type=int, default=0)
        food_carbs = request.form.get('food_carbs', type=int, default=0)
        food_fat = request.form.get('food_fat', type=int, default=0)
        food_cals = request.form.get('food_cal', type=int, default=0)
        # # EDIT FOODS TABLE
        helper.edit_food(db=db, food_id=food_id, food_name=food_name, protein=food_protein, carbs=food_carbs, fat=food_fat, calories=food_cals)
        return redirect(url_for('food_catalogue'))
    # # GET REQUEST
    food = dict(helper.query_food(db=db, food_id=food_id))
    return render_template('edit_food.html',
                           title='Edit Food',
                           food=food)


@app.route('/add_food', methods=['GET', 'POST'])
def add_food():
    """
    Add food to the food table in the database
    """
    # # GET DB INSTANCE
    db = get_db()
    # # POST REQUEST
    if request.method == 'POST':
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
            helper.delete_food(db=db, id=food_id, date=date)
            return redirect(url_for('add_day', date=date))
        # # ADD FOOD TO A DATE INTAKE
        food_id = request.form.get('food', type=str)
        date = request.form.get('date', type=str)
        helper.insert_intake(db=db, food_id=food_id, date=date)
        return redirect(url_for('add_day', date=date))
    date = request.args.get('date', type=str, default=None)
    # # NO DATE WAS PROVIDED BY THE USER
    if date is None or date == '':
        # # REDIRECT THE USER BACK TO THE HOME PAGE
        return redirect(url_for('home'))
    # # QUERY THE DB FOR THE PROVIDED DATE
    result = helper.query_db_date(db=db, date=date)
    # # QUERY THE DB FOR ALL THE AVAILABLE FOODS
    foods = helper.query_all_foods(db=db)
    aggregate = helper.aggregate_values(db=db, result=result)
    return render_template('add_day.html',
                           title='Add Day',
                           date=date,
                           foods=foods,
                           result=result,
                           aggregate=aggregate)


if __name__ == "__main__":
    app.run()
