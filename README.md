---

📊 Landbank Customer Information Management System (CIMS)

A secure, relational, web-based Customer Information Management System built with Flask and MySQL, designed for managing customer records for financial institutions.


---

🚀 Features

🔐 Admin & User Authentication

Separate roles for admin and customers.

Secure login using credentials stored in credentials table.


👤 Customer Records Management

Full capture of personal, financial, employment, spouse, bank, and affiliation details.

Auto-generation of user credentials.


🧱 Normalized Relational Database

Foreign key constraints with ON DELETE CASCADE to keep data consistent.


📐 Clean Modular Structure

Separation of concerns between UI, backend, and logic for maintainability.




---

🛠️ Technologies Used

Layer	Stack

Backend	Python (Flask)
Frontend	HTML, CSS, JavaScript, Bootstrap
Database	MySQL
Connector	mysql-connector-python



---

⚙️ Setup Instructions

1. ✅ Prerequisites

Python 3.x – Download

MySQL Server – Download

pip (Python package manager)



---

2. 🧱 MySQL Database Setup

a. Create the Database

CREATE DATABASE IF NOT EXISTS database_landbank;
USE database_landbank;

b. Create the Tables

-- occupation table
CREATE TABLE IF NOT EXISTS occupation (
    occ_id VARCHAR(10) PRIMARY KEY,
    occ_type VARCHAR(100) NOT NULL,
    bus_nature VARCHAR(300) NOT NULL,
    CHECK (occ_type IN (
        'Employed', 'Self-employed', 'OFW/Overseas Filipino', 'Retired', 'Farmer/Fisher',
        'Student/Minor', 'Unemployed', 'Housewife', 'Lawyers/Notary/Independent Legal Professional/Accountant',
        'Government Official'
    ))
);

-- financial_record table
CREATE TABLE IF NOT EXISTS financial_record (
    fin_code VARCHAR(10) PRIMARY KEY,
    source_wealth VARCHAR(150) NOT NULL,
    mon_income VARCHAR(50) NOT NULL,
    ann_income VARCHAR(50) NOT NULL,
    CHECK (mon_income IN (
        'Php 30,000.00 and below', 'Php 30,000.01-50,000.00', 'Php 50,000.01-100,000.00',
        'Php 100,000.01-500,000.00', 'Over Php 500,000.00'
    )),
    CHECK (ann_income IN (
        'Php 360,000.00 and below', 'Php 360,000.01-600,000.00', 'Php 600,000.01-1,200,000.00',
        'Php 1,200,000.01-6,000,000.00', 'Over Php 6,000,000.00'
    ))
);

-- employer_details table
CREATE TABLE IF NOT EXISTS employer_details (
    emp_id VARCHAR(10) PRIMARY KEY,
    tin_id VARCHAR(20) NOT NULL UNIQUE,
    empname VARCHAR(100) NOT NULL,
    emp_address VARCHAR(100) NOT NULL,
    phonefax_no VARCHAR(25) NOT NULL,
    job_title VARCHAR(50) NOT NULL,
    emp_date DATE NOT NULL
);

-- customer table
CREATE TABLE IF NOT EXISTS customer (
    cust_no VARCHAR(10) PRIMARY KEY,
    custname VARCHAR(50) NOT NULL,
    datebirth DATE NOT NULL,
    nationality VARCHAR(20) NOT NULL,
    citizenship VARCHAR(20) NOT NULL,
    custsex VARCHAR(10) NOT NULL,
    placebirth VARCHAR(20) NOT NULL,
    civilstatus VARCHAR(20) NOT NULL,
    num_children INT NOT NULL,
    mmaiden_name VARCHAR(50) NOT NULL,
    cust_address VARCHAR(100) NOT NULL,
    email_address VARCHAR(50) NOT NULL UNIQUE,
    contact_no VARCHAR(20) NOT NULL,
    occ_id VARCHAR(10),
    fin_code VARCHAR(10),
    password VARCHAR(255) NOT NULL,
    CONSTRAINT chk_custsex CHECK (custsex IN ('Male', 'Female')),
    CONSTRAINT chk_civilstatus CHECK (civilstatus IN ('Single', 'Married', 'Widowed', 'Divorced')),
    CONSTRAINT fk_customer_occ FOREIGN KEY (occ_id) REFERENCES occupation (occ_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_customer_fin FOREIGN KEY (fin_code) REFERENCES financial_record (fin_code) ON DELETE SET NULL ON UPDATE CASCADE
);

-- credentials table
CREATE TABLE IF NOT EXISTS credentials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cust_no VARCHAR(10) UNIQUE,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE
);

-- employment_details table
CREATE TABLE IF NOT EXISTS employment_details (
    empd INT AUTO_INCREMENT PRIMARY KEY,
    cust_no VARCHAR(10) NOT NULL UNIQUE,
    emp_id VARCHAR(10),
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (emp_id) REFERENCES employer_details(emp_id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- spouse table
CREATE TABLE IF NOT EXISTS spouse (
    sp_code VARCHAR(5) PRIMARY KEY,
    cust_no VARCHAR(10) NOT NULL,
    sp_name VARCHAR(100) NOT NULL,
    sp_datebirth DATE NOT NULL,
    sp_profession VARCHAR(50) NOT NULL,
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE ON UPDATE CASCADE
);

-- company_affiliation table
CREATE TABLE IF NOT EXISTS company_affiliation (
    cust_no VARCHAR(10) NOT NULL,
    depositor_role VARCHAR(30) NOT NULL,
    dep_compname VARCHAR(100) NOT NULL,
    PRIMARY KEY (cust_no, depositor_role, dep_compname),
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE ON UPDATE CASCADE
);

-- bank_details table
CREATE TABLE IF NOT EXISTS bank_details (
    bank_code VARCHAR(20) PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NOT NULL
);

-- existing_bank table
CREATE TABLE IF NOT EXISTS existing_bank (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cust_no VARCHAR(10) NOT NULL,
    bank_code VARCHAR(20) NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE,
    FOREIGN KEY (bank_code) REFERENCES bank_details(bank_code) ON DELETE CASCADE
);


---

3. 🔧 Configure app.py

Update your database config:

db_config = {
    'host': '127.0.0.1',
    'port': '3306',
    'user': 'root',
    'password': 'LandBank@2025',
    'database': 'database_landbank'
}

app.secret_key = 'your_super_secret_key_here'


---

4. 📦 Install Python Dependencies

pip install Flask mysql-connector-python


---

5. ▶️ Run the App

python app.py

Go to http://127.0.0.1:5000 in your browser.


---

🗂️ Project Structure

LandBank-CIMS/
│
├── app.py                  # Main backend logic
├── templates/              # HTML pages
├── static/                 # CSS, JS, assets
│   └── assets/             # Logos, icons, images
└── README.md               # This documentation


---

👨‍💼 Admin Login (Default)

Username: admin

Password: admin_password



---

📢 Developer Notes

Use ON DELETE CASCADE properly to keep data clean.

Hash passwords before storing (e.g. with bcrypt) in production.

Validate inputs to protect against SQL injection and XSS.

Backup your database regularly.



---

👤 Author

Jayson Combate
🔗 GitHub: @Jayson056 | @chi4ki1


---
