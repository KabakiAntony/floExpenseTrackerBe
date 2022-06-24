import os
from app.api import expenses
from app.api.model import db
from psycopg2.errors import (
    UniqueViolation,
    InvalidTextRepresentation,
    BadCopyFileFormat
 ) 
from flask import request, current_app, abort
from app.api.model.expense import (
    Expense,
    expenses_schema
)
from datetime import datetime
from dateutil import parser
from werkzeug.utils import secure_filename
from app.api.utils import (
    allowed_file,
    custom_make_response,
    token_required,
    convert_to_csv,
    add_expense_sys_id,
    generate_unique_string,
    save_csv_to_db,
    africa_nairobi_date_now
)


EXPENSE_FILE_FOLDER = os.environ.get('EXPENSE_FOLDER')


@expenses.route('/expenses/upload', methods=['POST'])
@token_required
def upload_Item(user):
    """
    upload batch expenses
    """
    receivedFile = request.files["newExpenseFile"]
    if receivedFile and allowed_file(receivedFile.filename):
        secureFilename = secure_filename(receivedFile.filename)
        filePath = os.path.join(
            current_app.root_path, EXPENSE_FILE_FOLDER, secureFilename)
        receivedFile.save(filePath)
        csvFile = convert_to_csv(filePath, EXPENSE_FILE_FOLDER)
        # add expense sys id  to csv
        expense_for = request.form['expense_for']
        add_expense_sys_id(csvFile, expense_for)

        try:
            # save expense csv to db
            save_csv_to_db(csvFile, 'public."Expense"')

            return custom_make_response(
                "data",
                "File uploaded successfully & expenses saved to database.",
                200
            )
        except UniqueViolation:
            db.session.rollback()
            return custom_make_response(
                "error",
                "Some of the items you are adding already exist,\
                    remove them and try again.",
                400
            )
        except InvalidTextRepresentation:
            db.session.rollback()
            return custom_make_response(
                "error",
                "Some of the columns in your file are empty, \
                    check them and try again.",
                400
            )
        except BadCopyFileFormat:
            db.session.rollback()
            return custom_make_response(
                "error",
                "Some of the data in the item column\
                    contains commas remove them and try\
                        again",
                400
            )

    return custom_make_response(
        "error",
        "Only excel files are allowed, select an excel file & try again.",
        400
    )


@expenses.route('/expenses', methods=['POST'])
@token_required
def create_expense(user):
    """" adding singular expenses on a daily basis"""
    try:
        expense_data = request.get_json()
        expense_sys_id = generate_unique_string()
        expense_for = expense_data['expense_for']
        purpose = expense_data['purpose']
        expense_client = expense_data['expense_client']
        amount = expense_data['amount']
        expense_date = africa_nairobi_date_now()

        new_expense = Expense(
            exp_id=expense_sys_id,
            exp_for=expense_for,
            purpose=purpose,
            exp_client=expense_client,
            amt=amount,
            exp_date=expense_date
        )
        db.session.add(new_expense)
        db.session.commit()

        return custom_make_response(
            "data",
            "Expense added successfully.",
            201
        )
    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@expenses.route('/expenses/<start_date>/<end_date>', methods=['GET'])
@token_required
def get_expenses(user, start_date, end_date):
    """
    this method will be used to get expenses for a given day
    and return the expense for that particular day in question
    """
    try:
        expense_data = (
            db.session.query(Expense)
            .filter(Expense.expense_date.between(
                f"{start_date}", f"{end_date}"))
            .all()
        )
        if not expense_data:
            abort(404, """
                No expenses have been found for today
                nor for the selected dates, add some 
                or change the date selection & try again
            """)
        daily_expenses = expenses_schema.dump(expense_data)

        return custom_make_response("data", daily_expenses, 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@expenses.route('/expenses/<expense_for>', methods=['GET'])
@token_required
def get_todays_expenses(user, expense_for):
    """
    this method will be used to get expenses for a given day,
    for the given person
    """
    try:
        todays_date = africa_nairobi_date_now()
        expense_data = Expense.query.filter_by(expense_for=expense_for).\
            filter_by(expense_date=todays_date).all()

        if not expense_data:
            abort(404, """
            You don't have any expenses today,
            add some and try again.
            """)
        daily_expenses = expenses_schema.dump(expense_data)

        return custom_make_response("data", daily_expenses, 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@expenses.route('/expenses/<id>', methods=['PATCH'])
@token_required
def update_expense(user, id):
    """
    make changes to an expense given its id
    """
    try:
        updated_expense_data = request.get_json()

        expense = Expense.query.filter_by(id=id).first()
        if not expense:
            abort(404, "The expense you are updating does not exist")

        Expense.query.filter_by(id=id).update(
            updated_expense_data
        )
        db.session.commit()

        return custom_make_response(
            "data",
            "Expense updated successfully.",
            200
        )
    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@expenses.route('/expenses/<id>', methods=['DELETE'])
@token_required
def delete_expense(user, id):
    """
    delete an expense given its id
    """
    try:
        expense = Expense.query.filter_by(id=id).first()
        if not expense:
            abort(404, "The expense you are deleting does not exist")

        Expense.query.filter_by(id=id).delete()
        db.session.commit()
        return custom_make_response(
            "data", "Expense deleted successfully.", 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@expenses.route('/expenses', methods=['GET'])
@token_required
def get_monies_to_foreman(user):
    """ get all monies given to foreman"""
    try:
        expense_data = Expense.query.filter_by(expense_for="flo").\
            filter_by(purpose="foreman").all()

        if not expense_data:
            abort(404, """
            You have not expensed money to foreman,
            expense some and try again.
            """)
        all_expenses = expenses_schema.dump(expense_data)

        return custom_make_response("data", all_expenses, 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@expenses.route('/expenses/foreman', methods=['GET'])
@token_required
def get_all_foreman_expenses(user):
    """ get all historical expenses by foreman """
    try:
        expense_data = Expense.query.filter_by(expense_for="foreman").all()

        if not expense_data:
            abort(404, """
            You have not expensed money to foreman,
            expense some and try again.
            """)
        all_expenses = expenses_schema.dump(expense_data)

        return custom_make_response("data", all_expenses, 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)

