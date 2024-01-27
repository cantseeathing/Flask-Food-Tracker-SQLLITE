from typing import List, Dict


def create_tables(db):
    """
    Creates the tables in the database if they don't already exist
    :param db: DB connection instance
    :return:
    """
    db.execute('''
        CREATE TABLE IF NOT EXISTS FOODS
            ( id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              protein INTEGER NOT NULL,
              carbohydrates INTEGER NOT NULL,
              fat INTEGER NOT NULL,
              calories INTEGER NOT NULL  )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS INTAKE
            ( date TEXT NOT NULL,
              id INTEGER PRIMARY KEY,
              food_id INTEGER NOT NULL REFERENCES FOODS(id) )
    ''')
    # # COMMIT THE CHANGES TO THE DATABASE
    db.commit()


def query_all_days(db) -> List:
    """
    Queries all days in the INTAKE table and returns the results
    :param db: DB connection instance
    :return: List of all results
    """
    cursor = db.execute("""
        SELECT * FROM INTAKE;
    """)
    # # FETCH ALL THE RESULTS
    results = cursor.fetchall()
    return results


def query_db_date(db, date: str) -> List:
    """
    Queries the INTAKE table for a specific date and returns the results as list
    :param db: DB connection instance
    :param date: Date to be queried as a string
    :return: List of all results
    """
    cursor = db.execute(f"""
        SELECT * FROM INTAKE 
            WHERE date = ?
    """, [date])
    # # FETCH ALL RESULTS
    results = cursor.fetchall()
    return results


def convert_result_to_dict(results: List) -> List:
    """
    Converts the results from the DB query to a list of dictionaries
    :param results: A list of sqlite3.Row objects
    :return: List of dictionaries
    """
    if len(results) == 0 or results[0] is None:
        return []
    return [dict(x) for x in results]


def query_all_foods(db) -> List:
    """
    Queries all food types from the FOODS table and returns the results
    :param db: DB connection instance
    :return: List of all food
    """
    cursor = db.execute("SELECT * FROM FOODS ORDER BY name ASC")
    # # FETCH ALL THE RESULTS
    results = cursor.fetchall()
    return results

print('requirments')
def insert_food(*args, **kwargs):
    """
    Inserts a new food type into the FOODS table
    :param args: name, protein, carbohydrate, fat, and calories values of the food type
    :param kwargs: db: DB connection instance
    :return:
    """
    db = kwargs.get('db')
    db.execute("""
        INSERT INTO FOODS (name, protein, carbohydrates, fat, calories)
        VALUES (?, ?, ?, ?, ?)
    """, [args[0], args[1], args[2], args[3], args[4]])
    # # COMMIT THE CHANGES TO THE DB
    db.commit()


def insert_intake(**kwargs):
    """
    Inserts a new food intake into the INTAKES table
    :param kwargs: db: DB connection instance, date: to query intake table, food_id: food id from the foods table
    :return:
    """
    db = kwargs.get('db')
    date = kwargs.get('date')
    food_id = kwargs.get('food_id')
    db.execute("""
        INSERT INTO INTAKE (date, food_id)
        VALUES (?, ?)
    """, [date, food_id])
    db.commit()


def query_food(db, food_id: int) -> List:
    """
    Queries the FOODS table and returns the results
    :param db: DB connection instance
    :param food_id: food_id from the foods table
    :return: List of the results of the query
    """
    cursor = db.execute(f"""
        SELECT * FROM FOODS
            WHERE id = '{food_id}';
    """)
    results = cursor.fetchone()
    return results


def get_all_dates(db) -> List:
    """
    Queries the INTAKE table to get all the dates
    :param db: DB connection instance
    :return: List of all available dates
    """
    cursor = db.execute("""
        SELECT DISTINCT date FROM INTAKE ORDER BY date DESC;
    """)
    result = cursor.fetchall()
    return result


def edit_food(**kwargs):
    """
    Edits food in the FOODS table using food_id
    :param kwargs: db: DB connection instance, food_name, protein, carbs, fat, calories, food_id values
    :return: 
    """
    db = kwargs.get('db')
    db.execute(f"""
        UPDATE FOODS
            SET name = ?, protein = ?, carbohydrates = ?, fat = ?, calories = ?
        WHERE id = ?
    """, [kwargs['food_name'], kwargs['protein'], kwargs['carbs'], kwargs['fat'], kwargs['calories'],
          kwargs['food_id']])
    db.commit()


def delete_food(db, id: int, date: str):
    """
    Deletes food from the INTAKES table
    :param db: DB connection instance
    :param id: id in the INTAKES table
    :param date: date to query the INTAKE table
    :return: 
    """
    db.execute(f"""
        DELETE FROM INTAKE WHERE id = '{id}' AND date = '{date}';
    """)
    db.commit()


def aggregate_values(db, result: List) -> Dict:
    """
    Aggregates the total nutrition values for the list of foods given
    :param db: DB connection instance
    :param result: List of foods to aggregate
    :return: Dictionary with the total nutrition values
    """
    agg_values = {
        "count": 0,
        "fat": 0,
        "protein": 0,
        "carbs": 0,
        "calories": 0,
    }
    if len(result) == 0 or result[0] is None:
        return agg_values
    for food in convert_result_to_dict(result):
        temp_food = dict(query_food(db=db, food_id=food.get('food_id')))
        agg_values["count"] += 1
        agg_values["fat"] += temp_food.get('fat')
        agg_values["protein"] += temp_food.get('protein')
        agg_values["carbs"] += temp_food.get('carbohydrates')
        agg_values["calories"] += temp_food.get('calories')
    return agg_values
