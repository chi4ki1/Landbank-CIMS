```markdown
# Landbank Customer Information Management System (CIMS)

This project is a web-based Customer Information Management System (CIMS) developed using Flask and MySQL. It allows administrators to manage customer records, including their personal, financial, employment, and relational details.

## Features

* **Admin Authentication:** Secure login for administrators.
* **Customer Management:**
    * View all customer records.
    * Add new customer records with detailed information.
    * Edit existing customer records.
    * Delete customer records and all associated data (handles foreign key constraints).
* **Database Integration:** Uses MySQL to store and manage customer data.

## Technologies Used

* **Backend:** Flask (Python)
* **Database:** MySQL
* **Frontend:** HTML, CSS, JavaScript (Bootstrap for styling)
* **Database Connector:** `mysql-connector-python`

## Setup Instructions

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

* **Python 3.x:** Make sure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).
* **MySQL Server:** Install MySQL Server. You can download it from [dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/).
* **pip:** Python package installer (usually comes with Python).

### 2. Database Configuration

1.  **Create a MySQL Database:**
    Open your MySQL client (e.g., MySQL Workbench, command line) and create a new database. The default database name used in `app.py` is `database_landbank`.

    ```sql
    CREATE DATABASE database_landbank;
    USE database_landbank;
    ```

2.  **Create Database Tables:**
    You'll need to create the necessary tables for your CIMS. Based on the `delete_customer` route and the code's logic, the following tables are expected. *Please ensure you define appropriate data types, primary keys, and foreign keys for each table.*

    Here's an example of the table schema based on the provided code (you may need to adjust data types and constraints based on your exact requirements):

    ```sql
    -- customer table (Parent table)
    CREATE TABLE customer (
        cust_no VARCHAR(255) PRIMARY KEY,
        custname VARCHAR(255),
        email_address VARCHAR(255),
        contact_no VARCHAR(20),
        fin_code VARCHAR(255), -- Foreign key to financial_record
        occ_id VARCHAR(255) -- Foreign key to occupation
        -- Add other customer-related fields here
    );

    -- credentials table (Child of customer)
    CREATE TABLE credentials (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cust_no VARCHAR(255) UNIQUE,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) DEFAULT 'user', -- e.g., 'admin', 'user'
        FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE
    );

    -- cust_po_relationship table (Child of customer)
    CREATE TABLE cust_po_relationship (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cust_no VARCHAR(255),
        relationship_details TEXT,
        FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE
    );

    -- existing_bank table (Child of customer)
    CREATE TABLE existing_bank (
        bank_id INT AUTO_INCREMENT PRIMARY KEY,
        cust_no VARCHAR(255),
        bank_name VARCHAR(255),
        account_number VARCHAR(255),
        FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE
    );

    -- company_affiliation table (Child of customer)
    CREATE TABLE company_affiliation (
        affiliation_id INT AUTO_INCREMENT PRIMARY KEY,
        cust_no VARCHAR(255),
        company_name VARCHAR(255),
        position VARCHAR(255),
        FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE
    );

    -- employment_details table (Child of customer, Parent of employer_details)
    CREATE TABLE employment_details (
        emp_id VARCHAR(255) PRIMARY KEY, -- This emp_id is generated and used for employer_details
        cust_no VARCHAR(255),
        employment_status VARCHAR(50),
        FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE
    );

    -- employer_details table (Child of employment_details)
    CREATE TABLE employer_details (
        employer_detail_id INT AUTO_INCREMENT PRIMARY KEY,
        emp_id VARCHAR(255),
        employer_name VARCHAR(255),
        employer_address VARCHAR(255),
        FOREIGN KEY (emp_id) REFERENCES employment_details(emp_id) ON DELETE CASCADE
    );

    -- spouse table (Child of customer)
    CREATE TABLE spouse (
        spouse_id INT AUTO_INCREMENT PRIMARY KEY,
        cust_no VARCHAR(255),
        spouse_name VARCHAR(255),
        FOREIGN KEY (cust_no) REFERENCES customer(cust_no) ON DELETE CASCADE
    );

    -- financial_record table (Parent of customer via fin_code)
    CREATE TABLE financial_record (
        fin_code VARCHAR(255) PRIMARY KEY,
        source_of_wealth VARCHAR(255),
        monthly_income DECIMAL(10, 2),
        annual_income DECIMAL(10, 2)
        -- Add other financial fields
    );

    -- occupation table (Parent of customer via occ_id)
    CREATE TABLE occupation (
        occ_id VARCHAR(255) PRIMARY KEY,
        occupation_name VARCHAR(255),
        industry VARCHAR(255)
        -- Add other occupation fields
    );

    -- Add an admin user for testing
    INSERT INTO credentials (username, password, role) VALUES ('admin', 'admin_password', 'admin');
    -- IMPORTANT: Change 'admin_password' to a strong hashed password in a real application.
    ```

3.  **Update Database Connection in `app.py`:**
    Open `app.py` and modify the `db_config` dictionary with your MySQL credentials:

    ```python
    db_config = {
        'host': '127.0.0.1',  # Or your database host IP/name
        'port': '3306',       # Your MySQL port
        'user': 'root',       # Your MySQL username
        'password': 'LandBank@2025',  # Your MySQL password
        'database': 'database_landbank' # The database you created
    }
    ```

    Also, change `app.secret_key` to a strong, unique secret key for security:
    ```python
    app.secret_key = 'your_super_secret_key_here' # IMPORTANT: Change this!
    ```

### 3. Install Dependencies

Navigate to your project's root directory in the terminal and install the required Python packages:

```bash
pip install Flask mysql-connector-python
```

### 4. Run the Application

From the project's root directory, run the Flask application:

```bash
python app.py
```

The application will start, and you should see output similar to this:

```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on [http://0.0.0.0:0000](http://0.0.0.0:0000) (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: XXX-XXX-XXX
```
(Note: The port `0000` is a placeholder in your provided code; Flask typically runs on `5000` by default if no port is specified, or you can explicitly set it to `5000` or another available port).

### 5. Access the Application

Open your web browser and go to the address provided in the terminal, usually `http://127.0.0.1:5000` or `http://localhost:5000`.

You can log in using the admin credentials you inserted into the `credentials` table (e.g., username: `admin`, password: `admin_password`).

## Project Structure

* `app.py`: The main Flask application file containing routes, database interactions, and business logic.
* `templates/`: Directory for HTML template files (e.g., `admin_dashboard.html`, `login.html`, `admin_edit_customer.html`).
* `static/`: Directory for static files like CSS, JavaScript, and images.

---
```