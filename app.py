# app.py
from flask import Flask, render_template, request, redirect
import mysql.connector
from config import db_config

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customers')
def customer_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Customer")
    customers = cursor.fetchall()
    conn.close()
    return render_template('customer_list.html', customers=customers)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()

    # Generate unique codes using NULL insertion
    cursor.execute("INSERT INTO SpouseCode () VALUES ()")
    spouse_code = cursor.lastrowid

    cursor.execute("INSERT INTO Occupation () VALUES ()")
    occ_id = cursor.lastrowid

    cursor.execute("INSERT INTO FinancialRecord () VALUES ()")
    fin_code = cursor.lastrowid

    # Insert customer info
    cursor.execute("""
        INSERT INTO Customer (
            cust_no, custname, datebirth, nationality, citizenship,
            custsex, placebirth, civilstatus, num_children, mmaiden_name,
            cust_address, email_address, contact_no,
            spouse_code, occ_id, fin_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['cust_no'], data['custname'], data['datebirth'], data['nationality'], data['citizenship'],
        data['custsex'], data['placebirth'], data['civilstatus'], data['num_children'], data['mmaiden_name'],
        data['cust_address'], data['email_address'], data['contact_no'],
        spouse_code, occ_id, fin_code
    ))

    conn.commit()
    conn.close()
    return redirect('/customers')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=0000, debug=True)  # Set a valid port number (e.g., 5000)
