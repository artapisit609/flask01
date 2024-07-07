from flask import Flask, render_template, url_for
import pymysql

app = Flask(__name__)

def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='1023-a10',
        database='expense',
        cursorclass=pymysql.cursors.DictCursor
    )

def format_currency(amount):
    return "{:,.2f}".format(amount)

@app.route('/')
def homepage():
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            # Total balance from bookbank
            cursor.execute("SELECT SUM(bankqty) AS total_balance FROM bookbank")
            total_balance = cursor.fetchone()['total_balance'] or 0

            # Total balance from book_out
            cursor.execute("SELECT SUM(qout) AS total_out FROM book_out")
            total_out = cursor.fetchone()['total_out'] or 0

            # Total monthly expense from book_m
            cursor.execute("SELECT SUM(m_qty) AS total_monthly_expense FROM book_m")
            total_monthly_expense = cursor.fetchone()['total_monthly_expense'] or 0

            # Calculate updated total balance after deducting total expense
            total_remain = total_balance - total_out

            # Calculate months remaining based on total balance and total monthly expense
            if total_monthly_expense != 0:
                months_remaining = total_balance / total_monthly_expense
            else:
                months_remaining = float('inf')  # Handle division by zero

            # Check if months remaining is less than or equal to 1
            months_remaining_style = 'color: red;' if months_remaining <= 1 else ''

    finally:
        connection.close()

    return render_template(
        'homepage.html',
        total_monthly_expense=format_currency(total_monthly_expense),
        total_balance=format_currency(total_balance),
        total_remain=format_currency(total_remain),
        months_remaining=format_currency(months_remaining),
        months_remaining_style=months_remaining_style
    )

@app.route('/bookbank')
def bookbank():
    connection = connect_db()
    bookbank_data = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_bb, bankname, bankqty FROM bookbank")
            bookbank_data = cursor.fetchall()
    finally:
        connection.close()

    return render_template('bookbank.html', bookbank_data=bookbank_data)

@app.route('/book_in_data')
def book_in_data():
    connection = connect_db()
    book_in_data = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM book_in")
            book_in_data = cursor.fetchall()
    finally:
        connection.close()

    return render_template('book_in_data.html', book_in_data=book_in_data)

@app.route('/book_out_data')
def book_out_data():
    connection = connect_db()
    book_out_data = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM book_out")
            book_out_data = cursor.fetchall()
    finally:
        connection.close()

    return render_template('book_out_data.html', book_out_data=book_out_data)

@app.route('/listmonth')
def listmonth():
    connection = None
    try:
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM book_m")
            book_m_data = cursor.fetchall()

            cursor.execute("SELECT SUM(m_qty) AS total_quantity FROM book_m")
            total_quantity = cursor.fetchone()['total_quantity'] or 0
    finally:
        if connection:
            connection.close()

    return render_template('listmonth.html', book_m_data=book_m_data, total_quantity=total_quantity)

@app.route('/listyear')
def listyear():
    connection = None
    try:
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_py, y_list, y_qty, y_month FROM book_y ORDER BY FIELD(y_month, 'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม')")
            book_y_data = cursor.fetchall()

            cursor.execute("SELECT SUM(y_qty) AS total_quantity FROM book_y")
            total_quantity = cursor.fetchone()['total_quantity'] or 0
    finally:
        if connection:
            connection.close()

    return render_template('listyear.html', book_y_data=book_y_data, total_quantity=total_quantity)

@app.route('/result_mbank')
def result_mbank():
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            query = "SELECT m_bank, SUM(m_qty) as total_qty FROM book_m GROUP BY m_bank ORDER BY total_qty DESC"
            cursor.execute(query)
            results = cursor.fetchall()
    finally:
        connection.close()
    
    return render_template('result_mbank.html', results=results)

if __name__ == '__main__':
    app.run(app.run(debug=True))