from model import *
from datetime import date
import datetime

def this_week_start_date():
    start_date = date.today() - datetime.timedelta(days=(date.today().weekday()+1))
    return start_date


def meal_plan_days(start_date):

    all_days = [start_date,
                    start_date + datetime.timedelta(days=1),
                    start_date + datetime.timedelta(days=2),
                    start_date + datetime.timedelta(days=3),
                    start_date + datetime.timedelta(days=4),
                    start_date + datetime.timedelta(days=5),
                    start_date + datetime.timedelta(days=6)]
    return all_days


def get_week_id(user_id, start_date):
    if Week.query.filter(Week.user_id==user_id,
                            Week.start_date==start_date).all() == []:
        return False
    else:
        return Week.query.filter(Week.user_id==user_id,
                            Week.start_date==start_date).one().week_id


def create_new_week(user, start_date):

    week = Week(user_id=user.user_id, start_date=start_date)
    all_days = meal_plan_days(start_date)

    db.session.add(week)
    db.session.commit()
    week_id = week.week_id

    for meal_date in week.plan_days():
        add_meal_entries(week_id, meal_date)


def add_meal_entries(week_id, meal_date):
    m01 = Meal(week_id=week_id, meal_type_id="br", meal_date=meal_date)
    m02 = Meal(week_id=week_id, meal_type_id="lu", meal_date=meal_date)
    m03 = Meal(week_id=week_id, meal_type_id="din", meal_date=meal_date)
    m04 = Meal(week_id=week_id, meal_type_id="snck", meal_date=meal_date)

    db.session.add_all([m01, m02, m03, m04])
    db.session.commit()


def create_meal_plan(week_id, all_days):
    meal_plan_list = []

    breakfast = create_meal_dict(week_id, "br")
    lunch = create_meal_dict(week_id, "lu")
    dinner = create_meal_dict(week_id, "din")
    snacks = create_meal_dict(week_id, "snck")

    meal_plan_list.append(breakfast)
    meal_plan_list.append(lunch)
    meal_plan_list.append(dinner)
    meal_plan_list.append(snacks)

    return meal_plan_list


def create_meal_dict(week_id, meal_type_id):
    meals_list = Meal.query.filter(Meal.week_id==week_id,
            Meal.meal_type_id==meal_type_id).order_by(Meal.meal_date).all()
    meals_dict = {}
    meals_dict["meal_type"] = MealType.query.filter(
                        MealType.meal_type_id==meal_type_id).one().type_name

    i = 1
    for meal in meals_list:
        recipe_list = meal.recipes
        while len(recipe_list) < 4:
            recipe_list = recipe_list + ['']
        meals_dict["day" + str(i)] = recipe_list
        i += 1

    return meals_dict


def edit_meals(meal_type_id, recipe_list, week_id, meal_date):
    meal_id = Meal.query.filter(Meal.week_id==week_id,
                                Meal.meal_type_id==meal_type_id,
                                Meal.meal_date==meal_date).one().meal_id
    for r_id in recipe_list:
        if MealRecipe.query.filter(MealRecipe.meal_id==meal_id,
                                    MealRecipe.recipe_id==r_id).all() == []:
            new_meal_recipe = MealRecipe(recipe_id=r_id, meal_id=meal_id)
            db.session.add(new_meal_recipe)

    db.session.commit()


##############################################################################
# Helper functions

def connect_to_db(app):

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mealplan'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":


    from server import app
    connect_to_db(app)
    print ("Connected to DB.")
