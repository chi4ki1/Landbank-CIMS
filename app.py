# START OF MODIFICATIONS - PART 1

import mysql.connector, os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import uuid
from werkzeug.utils import secure_filename
from flask import make_response
from werkzeug.security import generate_password_hash, check_password_hash # ADD THIS NEW IMPORT

app = Flask(__name__)

# IMPORTANT: Load secret key from environment variable for production
# If FLASK_SECRET_KEY is not set, it will fall back to a default (change in production!)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_super_secret_key_here') # UPDATE THIS LINE
# For development, you can keep 'your_super_secret_key_here' as a fallback.
# For production, set this environment variable:
# On Linux/macOS: export FLASK_SECRET_KEY='a_very_long_and_random_string'
# On Windows (Cmd): set FLASK_SECRET_KEY=a_very_long_and_random_string
# On Windows (PowerShell): $env:FLASK_SECRET_KEY='a_very_long_and_random_string'

# END OF MODIFICATIONS - PART 1

# Database configuration
db_config = {
    'host': '127.0.0.1',  # Use 127.0.0.1 for local MySQL, or your database host
    'port': '3306',
    'user': 'root',
    'password': 'LandBank@2025',  # Your MySQL root password
    'database': 'database_landbank'
}

def get_db_connection():
    """Establishes and returns a database connection using mysql.connector."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# --- Function to Ensure Database Schema (for development/initial setup) ---
def _ensure_database_schema():
    """
    Ensures that necessary database columns have appropriate lengths and types (VARCHAR for IDs).
    This function should typically be run only once, or managed by a proper migration tool.
    For development, it runs on app startup.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to get database connection for schema update.")
            return

        cursor = conn.cursor()
        print("Attempting to ensure database schema (column lengths and types)...\n")

        # Define schema for relevant tables and columns, explicitly setting VARCHAR lengths
        schema_updates = {
            'customer': {
                'cust_no': 'VARCHAR(10) NOT NULL PRIMARY KEY',
                'custname': 'VARCHAR(255)',
                'email_address': 'VARCHAR(255)',
                'contact_no': 'VARCHAR(20)',
                'occ_id': 'VARCHAR(10)',
                'fin_code': 'VARCHAR(10)'
            },
            'occupation': {
                'occ_id': 'VARCHAR(10) NOT NULL PRIMARY KEY',
                'occ_type': 'VARCHAR(255)',
                'bus_nature': 'VARCHAR(255)'
            },
            'financial_record': {
                'fin_code': 'VARCHAR(10) NOT NULL PRIMARY KEY',
                'source_wealth': 'VARCHAR(255)',
                'mon_income': 'VARCHAR(255)', # Ensure this is VARCHAR
                'ann_income': 'VARCHAR(255)'  # Ensure this is VARCHAR
            },
            'credentials': {
                'cust_no': 'VARCHAR(10) NOT NULL',
                'username': 'VARCHAR(255)',
                'password': 'VARCHAR(255)'
            },
            'employer_details': {
                'emp_id': 'VARCHAR(10) NOT NULL PRIMARY KEY',
                'occ_id': 'VARCHAR(10)',
                'tin_id': 'VARCHAR(50)',
                'empname': 'VARCHAR(255)',
                'emp_address': 'VARCHAR(255)',
                'phonefax_no': 'VARCHAR(50)',
                'job_title': 'VARCHAR(255)',
                'emp_date': 'DATE'
            },
            'public_official_details': {
                'gov_int_id': 'VARCHAR(10) NOT NULL PRIMARY KEY',
                'gov_int_name': 'VARCHAR(255)',
                'official_position': 'VARCHAR(255)',
                'branch_orgname': 'VARCHAR(255)'
            },
            'cust_po_relationship': {
                'relation_desc': 'VARCHAR(255)' # Ensure this is VARCHAR
            },
            'spouse': {
                'cust_no': 'VARCHAR(10)',
                'sp_name': 'VARCHAR(255)',
                'sp_datebirth': 'DATE',
                'sp_profession': 'VARCHAR(255)'
            },
            'company_affiliation': {
                'cust_no': 'VARCHAR(10)',
                'depositor_role': 'VARCHAR(255)',
                'dep_compname': 'VARCHAR(255)'
            },
            'bank_details': {
                'bank_code': 'VARCHAR(10) NOT NULL PRIMARY KEY',
                'bank_name': 'VARCHAR(255)',
                'branch': 'VARCHAR(255)'
            },
            'existing_bank': {
                'cust_no': 'VARCHAR(10)',
                'bank_code': 'VARCHAR(10)',
                'acc_type': 'VARCHAR(255)'
            },
            'employment_details': {
                'cust_no': 'VARCHAR(10)',
                'emp_id': 'VARCHAR(10)'
            }
        }

        for table, columns in schema_updates.items():
            try:
                # Check if table exists
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                table_exists = cursor.fetchone()

                if not table_exists:
                    print(f"  - WARNING: Table '{table}' does not exist. Skipping schema update for this table.")
                    continue

                cursor.execute(f"DESCRIBE {table}")
                existing_columns_info = cursor.fetchall()
                existing_columns_map = {col[0]: {'type': col[1].decode('utf-8').upper(), 'null': col[2].decode('utf-8').upper(), 'key': col[3].decode('utf-8').upper()} for col in existing_columns_info}

                for col_name, desired_col_def in columns.items():
                    if col_name in existing_columns_map:
                        existing_type_info = existing_columns_map[col_name]
                        # Simplified check for VARCHAR type and length, and NOT NULL/PRIMARY KEY
                        # This comparison is robust for exact type match (e.g., VARCHAR(10) vs VARCHAR(20))
                        if existing_type_info['type'] != desired_col_def.upper().split(' ')[0] and 'VARCHAR' in desired_col_def.upper():
                             # Special handling for VARCHAR where length might differ but type is still VARCHAR
                             current_type_base = existing_type_info['type'].split('(')[0]
                             desired_type_base = desired_col_def.split('(')[0].upper()
                             if current_type_base == desired_type_base:
                                 # If base type is VARCHAR, check full definition (e.g., VARCHAR(10) vs VARCHAR(255))
                                 if existing_type_info['type'] != desired_col_def.upper():
                                     try:
                                         cursor.execute(f"ALTER TABLE {table} MODIFY COLUMN {col_name} {desired_col_def};")
                                         print(f"  - Altered {table}.{col_name} to {desired_col_def} (type/length mismatch corrected)")
                                     except mysql.connector.Error as alter_err:
                                         print(f"  - WARNING: Could not alter {table}.{col_name} for type/length: {alter_err}")
                                 else:
                                     print(f"  - {table}.{col_name} already matches '{desired_col_def}'")
                             else: # Different base type (e.g., INT to VARCHAR)
                                 try:
                                     cursor.execute(f"ALTER TABLE {table} MODIFY COLUMN {col_name} {desired_col_def};")
                                     print(f"  - Altered {table}.{col_name} to {desired_col_def} (base type changed)")
                                 except mysql.connector.Error as alter_err:
                                     print(f"  - WARNING: Could not alter {table}.{col_name} for base type: {alter_err}")
                        elif existing_type_info['type'] != desired_col_def.upper(): # For non-VARCHAR or exact type check
                            try:
                                cursor.execute(f"ALTER TABLE {table} MODIFY COLUMN {col_name} {desired_col_def};")
                                print(f"  - Altered {table}.{col_name} to {desired_col_def}")
                            except mysql.connector.Error as alter_err:
                                print(f"  - WARNING: Could not alter {table}.{col_name}: {alter_err}")
                        else:
                            print(f"  - {table}.{col_name} already matches '{desired_col_def}'")
                    else:
                        print(f"  - WARNING: Column '{col_name}' not found in table '{table}'. Skipping alter for this column.")

            except mysql.connector.Error as desc_err:
                print(f"  - WARNING: Error describing table {table}: {desc_err}")
            except Exception as e:
                print(f"  - AN UNEXPECTED ERROR occurred while processing table {table}: {e}")

        conn.commit()
        print("\nDatabase schema check/update completed.")
    except mysql.connector.Error as err:
        print(f"Error during database schema update: {err}")
    except Exception as e:
        print(f"An unexpected error occurred during schema update: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def no_cache(view):
    def no_cache_wrapper(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    no_cache_wrapper.__name__ = view.__name__
    return no_cache_wrapper


# START OF MODIFICATIONS - PART 2: NEW HELPER FUNCTIONS

def generate_next_cust_no(cursor):
    """
    Generates the next sequential customer number (e.g., C001, C002, ..., C015, C016).
    Assumes cust_no always starts with 'C' followed by numbers.
    """
    try:
        cursor.execute("SELECT MAX(CAST(SUBSTRING(cust_no, 2) AS UNSIGNED)) AS max_cust_num FROM customer")
        result = cursor.fetchone()
        
        max_num = result['max_cust_num'] if result and result['max_cust_num'] is not None else 0
        
        next_num = max_num + 1
        
        # Format the number with leading zeros to ensure three digits (e.g., 1 -> 001, 15 -> 015)
        new_cust_no = f"C{next_num:03d}"
        
        return new_cust_no
    except Exception as e:
        print(f"Error generating next cust_no: {e}")
        return None

def get_or_insert_occupation(cursor, occ_type, bus_nature):
    """
    Checks if an occupation with the given type and nature exists.
    If yes, returns its occ_id. If no, inserts a new occupation,
    generates a new occ_id, and returns it.
    """
    cursor.execute("SELECT occ_id FROM occupation WHERE occ_type = %s AND bus_nature = %s", (occ_type, bus_nature))
    result = cursor.fetchone()
    if result:
        return result['occ_id']
    else:
        cursor.execute("SELECT MAX(CAST(SUBSTRING(occ_id, 3) AS UNSIGNED)) AS max_occ_num FROM occupation")
        max_num_res = cursor.fetchone()
        max_num = max_num_res['max_occ_num'] if max_num_res and max_num_res['max_occ_num'] is not None else 0
        new_occ_id = f"OC{max_num + 1:02d}" # Format like OC01, OC02

        cursor.execute("INSERT INTO occupation (occ_id, occ_type, bus_nature) VALUES (%s, %s, %s)", (new_occ_id, occ_type, bus_nature))
        return new_occ_id

def get_or_insert_financial_record(cursor, source_wealth, mon_income, ann_income):
    """
    Checks if a financial record with the given details exists.
    If yes, returns its fin_code. If no, inserts a new record,
    generates a new fin_code, and returns it.
    """
    cursor.execute("SELECT fin_code FROM financial_record WHERE source_wealth = %s AND mon_income = %s AND ann_income = %s", (source_wealth, mon_income, ann_income))
    result = cursor.fetchone()
    if result:
        return result['fin_code']
    else:
        cursor.execute("SELECT MAX(CAST(SUBSTRING(fin_code, 2) AS UNSIGNED)) AS max_fin_num FROM financial_record")
        max_num_res = cursor.fetchone()
        max_num = max_num_res['max_fin_num'] if max_num_res and max_num_res['max_fin_num'] is not None else 0
        new_fin_code = f"F{max_num + 1}" # Format like F1, F2 (adjust to F01, F02 if preferred by changing f"F{max_num + 1:02d}")

        cursor.execute("INSERT INTO financial_record (fin_code, source_wealth, mon_income, ann_income) VALUES (%s, %s, %s, %s)", (new_fin_code, source_wealth, mon_income, ann_income))
        return new_fin_code

# END OF MODIFICATIONS - PART 2



# --- ROUTE: first landing page ---
@app.route('/')
def landing():
    """Renders the landing page."""
    return render_template('landing.html')

# ---ROUTE: home ---
@app.route('/home')
@no_cache
def home():
    if 'user' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('home.html')
# ---ROUTE: about ---
@app.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html')

# ---ROUTE: about ---
@app.route('/about-1')
def userabout():
    """Renders the about page."""
    return render_template('userabout.html')

# ---ROUTE: service ---
@app.route('/services')
def services():
    """Renders the services page."""
    return render_template('services.html')

@app.route('/services-1')
def userservices():
    """Renders the services page."""
    return render_template('userservices.html')

# ---ROUTE: contact ---
@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template('contact.html')

@app.route('/contact-1')
def usercontact():
    """Renders the contact page."""
    return render_template('usercontact.html')

# ---ROUTE: Registration Print ---
@app.route('/registrationPrint')
def registrationPrint():
    """Renders the registration print/summary page."""
    return render_template('registrationPrint.html')

# ---ROUTE: sign-up landing page ---
@app.route('/register')
def register():
    """Renders the registration page (initial entry point)."""
    return render_template('register.html')

# --- reg 1 ---
@app.route('/registration1', methods=['GET'])
def registration1():
    """Renders the first step of the registration form."""
    return render_template('registration1.html')

# ---ROUTE: reg 2 ---
@app.route('/registration2', methods=['GET'])
def registration2():
    """Renders the second step of the registration form."""
    return render_template('registration2.html')

# ---ROUTE: reg 3 ---
@app.route('/registration3', methods=['GET'])
def registration3():
    """Renders the third step of the registration form."""
    return render_template('registration3.html')

# ---ROUTE: Submit registration ---
@app.route('/submitRegistration', methods=['POST'])
def submit_registration():
    """
    Receives all registration data as JSON from the frontend (registration.js)
    and handles the complete database insertion, including credentials.
    Generates UUIDs for VARCHAR primary keys.
    """
    conn = None
    cursor = None
    try:
        # Get JSON data sent from the frontend
        data = request.get_json()
        r1 = data.get('registration1', {})
        r2 = data.get('registration2', {})
        r3 = data.get('registration3', {})

        conn = get_db_connection()
        if not conn:
            raise Exception("Database connection failed")

        cursor = conn.cursor()
        conn.start_transaction()

        # --- 1. Insert into occupation table ---
        # Generate a unique VARCHAR ID for occ_id
        occ_id = str(uuid.uuid4())[:10].upper() # Using uuid for VARCHAR ID
        occ_type = r2.get('occupation')
        bus_nature = r2.get('natureOfBusiness')
        sql_occ = "INSERT INTO occupation (occ_id, occ_type, bus_nature) VALUES (%s, %s, %s)"
        cursor.execute(sql_occ, (occ_id, occ_type, bus_nature))

        # --- 2. Insert into financial_record table ---
        # Generate a unique VARCHAR ID for fin_code
        fin_code = str(uuid.uuid4())[:10].upper() # Using uuid for VARCHAR ID
        source_wealth_list = r2.get('sourceOfWealth', [])
        source_wealth = ', '.join(source_wealth_list) if isinstance(source_wealth_list, list) else source_wealth_list
        mon_income = r2.get('monthlyIncome')
        ann_income = r2.get('annualIncome')
        sql_fin = "INSERT INTO financial_record (fin_code, source_wealth, mon_income, ann_income) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_fin, (fin_code, source_wealth, mon_income, ann_income))

        # --- 3. Insert into customer table ---
        # Generate a unique VARCHAR ID for cust_no
        cust_no = str(uuid.uuid4())[:10].upper() # Using uuid for VARCHAR ID
        custname = f"{r1.get('firstName', '')} {r1.get('lastName', '')}"
        datebirth = r1.get('dob')
        nationality = r1.get('nationality')
        citizenship = r1.get('citizenship')
        custsex = r1.get('sex')
        placebirth = r1.get('placeOfBirth')
        civilstatus = r1.get('civilStatus')
        num_children = int(r1.get('children', 0) or 0)
        mmaiden_name = r1.get('motherMaidenName')
        cust_address = r1.get('address')
        email_address = r1.get('email')
        contact_no = r1.get('telephone')

        sql_cust = """INSERT INTO customer (cust_no, custname, datebirth, nationality, citizenship, custsex, placebirth, civilstatus, num_children, mmaiden_name, cust_address, email_address, contact_no, occ_id, fin_code)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        customer_data = (
            cust_no, custname, datebirth, nationality, citizenship,
            custsex, placebirth, civilstatus,
            num_children,
            mmaiden_name, cust_address,
            email_address, contact_no, occ_id, fin_code
        )

        print("--- DEBUG: Preparing to execute customer insert query ---")
        # print("SQL Query:", cursor.mogrify(sql_cust, customer_data)) # Removed this line

        cursor.execute(sql_cust, customer_data)

        print(f"--- DEBUG: Successfully inserted customer. New cust_no: {cust_no} (Type: {type(cust_no)}) ---")

        # --- 4. Insert into employer_details and employment_details if applicable ---
        if r2.get('occupation') == 'Employed':
            # Generate a unique VARCHAR ID for emp_id
            emp_id = str(uuid.uuid4())[:10].upper() # Using uuid for VARCHAR ID
            tin_id = r2.get('tinId', '')
            empname = r2.get('companyName', '')
            emp_address = r2.get('employerAddress', '')
            phonefax_no = r2.get('employerPhone', '')
            job_title = r2.get('jobTitle', '')
            emp_date = r2.get('employmentDate') or '2000-01-01'

            sql_emp_details = "INSERT INTO employer_details (emp_id, occ_id, tin_id, empname, emp_address, phonefax_no, job_title, emp_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_emp_details, (emp_id, occ_id, tin_id, empname, emp_address, phonefax_no, job_title, emp_date))

            sql_emp_link = "INSERT INTO employment_details (cust_no, emp_id) VALUES (%s, %s)"
            cursor.execute(sql_emp_link, (cust_no, emp_id))


        # --- 5. Insert into spouse table if married ---
        if r1.get('civilStatus') == 'Married':
            sp_name = f"{r1.get('spouseFirstName', '')} {r1.get('spouseLastName', '')}"
            sp_datebirth = r1.get('spouseDob')
            sp_profession = r1.get('spouseProfession')
            if sp_name.strip() and sp_datebirth and sp_profession:
                sql_spouse = "INSERT INTO spouse (cust_no, sp_name, sp_datebirth, sp_profession) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_spouse, (cust_no, sp_name, sp_datebirth, sp_profession))

        # --- 6. Insert into company_affiliation ---
        roles = r3.get('depositorRole', [])
        companies = r3.get('companyName', [])
        if not isinstance(roles, list): roles = [roles] if roles else []
        if not isinstance(companies, list): companies = [companies] if companies else []

        for role, company in zip(roles, companies):
            if role and company:
                sql_comp_aff = "INSERT INTO company_affiliation (cust_no, depositor_role, dep_compname) VALUES (%s, %s, %s)"
                cursor.execute(sql_comp_aff, (cust_no, role, company))

        # --- 7. Insert into bank_details and existing_bank ---
        banks = r3.get('bank', [])
        branches = r3.get('branch', [])
        acc_types = r3.get('accountType', [])
        if not isinstance(banks, list): banks = [banks] if banks else []
        if not isinstance(branches, list): branches = [branches] if branches else []
        if not isinstance(acc_types, list): acc_types = [acc_types] if acc_types else []

        for bank_name, branch, acc_type in zip(banks, branches, acc_types):
            if bank_name and branch and acc_type:
                sql_insert_bank = "INSERT IGNORE INTO bank_details (bank_code, bank_name, branch) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert_bank, (bank_name, bank_name, branch))

                sql_existing_bank = "INSERT INTO existing_bank (cust_no, bank_code, acc_type) VALUES (%s, %s, %s)"
                cursor.execute(sql_existing_bank, (cust_no, bank_name, acc_type))

        # --- 8. Insert into public_official_details and cust_po_relationship ---
        gov_last_names = r3.get('govLastName', [])
        gov_first_names = r3.get('govFirstName', [])
        relationships = r3.get('relationship', [])
        positions = r3.get('position', [])
        org_names = r3.get('govBranchOrgName', [])

        if not isinstance(gov_last_names, list): gov_last_names = [gov_last_names] if gov_last_names else []
        if not isinstance(gov_first_names, list): gov_first_names = [gov_first_names] if gov_first_names else []
        if not isinstance(relationships, list): relationships = [relationships] if relationships else []
        if not isinstance(positions, list): positions = [positions] if positions else []
        if not isinstance(org_names, list): org_names = [org_names] if org_names else []

        min_len = min(len(gov_last_names), len(gov_first_names), len(relationships), len(positions), len(org_names))
        for i in range(min_len):
            if gov_last_names[i] and gov_first_names[i] and relationships[i] and positions[i] and org_names[i]:
                # Generate a unique VARCHAR ID for gov_int_id
                gov_int_id = str(uuid.uuid4())[:10].upper() # Using uuid for VARCHAR ID
                gov_name = f"{gov_first_names[i]} {gov_last_names[i]}"
                sql_po_details = "INSERT INTO public_official_details (gov_int_id, gov_int_name, official_position, branch_orgname) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_po_details, (gov_int_id, gov_name, positions[i], org_names[i]))

                sql_po_rel = "INSERT INTO cust_po_relationship (cust_no, gov_int_id, relation_desc) VALUES (%s, %s, %s)"
                cursor.execute(sql_po_rel, (cust_no, gov_int_id, relationships[i]))

        # --- 9. Call insert_credentials here to save username and password ---
        insert_credentials(cursor, cust_no, r1)

        conn.commit()
        return '', 200

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        print(f"Error during registration submission: {err}")
        return f"Database error during submission: {err}", 500
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Unexpected error during registration submission: {e}")
        return f"An unexpected error occurred: {e}", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Helper Function Definitions (Called from submit_registration) ---
# START OF MODIFICATIONS - PART 3: UPDATED insert_credentials

def insert_credentials(cursor, cust_no, data):
    """
    Inserts user credentials into the credentials table, hashing the password.
    Assumes `data` contains 'email' and a *plain-text* 'password' field.
    """
    username = data.get('email')
    plain_password = data.get('password')

    # Hash the password using werkzeug.security
    if plain_password:
        hashed_password = generate_password_hash(plain_password)
    else:
        # Handle case where no password is provided (e.g., generate a random one or raise error)
        # For now, let's hash an empty string or raise an error. Better to enforce password.
        hashed_password = generate_password_hash('') # Hashing an empty string
        print("Warning: No plain password provided for hashing in insert_credentials.")

    sql = """
        INSERT INTO credentials (cust_no, username, password)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (cust_no, username, hashed_password)) # Store the hashed password

# END OF MODIFICATIONS - PART 3

# --- UserHome after login---
@app.route('/userform')
def userform():
    if 'cust_no' not in session:
        flash('Please log in to access this page.', 'info')
        return redirect(url_for('login'))

    cust_no = session['cust_no']
    conn = None
    cursor = None
    user_data = {}

    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return render_template('login.html', error='Database connection failed.')

        cursor = conn.cursor(dictionary=True) # Use dictionary=True to fetch rows as dictionaries

        # Fetch Customer Information
        cursor.execute("""
            SELECT c.*, o.occ_type, o.bus_nature, f.source_wealth, f.mon_income, f.ann_income
            FROM customer c
            LEFT JOIN occupation o ON c.occ_id = o.occ_id
            LEFT JOIN financial_record f ON c.fin_code = f.fin_code
            WHERE c.cust_no = %s
        """, (cust_no,))
        user_data['customer'] = cursor.fetchone()

        if not user_data['customer']:
            flash('Customer data not found.', 'danger')
            return redirect(url_for('login'))

        # Fetch Occupation and Financial data directly from customer join (already done above)
        # Separate the fetched data for clarity in the template, though already joined
        user_data['occupation'] = {
            'occ_type': user_data['customer'].get('occ_type'),
            'bus_nature': user_data['customer'].get('bus_nature')
        }
        user_data['financial_record'] = {
            'source_wealth': user_data['customer'].get('source_wealth'),
            'mon_income': user_data['customer'].get('mon_income'),
            'ann_income': user_data['customer'].get('ann_income')
        }


        # Fetch Spouse Information (if exists)
        cursor.execute("SELECT * FROM spouse WHERE cust_no = %s", (cust_no,))
        user_data['spouse'] = cursor.fetchone()

        # Fetch Employer Details (if exists, linked via employment_details and occupation)
        # Check if the customer is 'Employed' before fetching employer details
        if user_data['occupation']['occ_type'] == 'Employed':
            cursor.execute("""
                SELECT ed.*
                FROM employer_details ed
                JOIN employment_details empd ON ed.emp_id = empd.emp_id
                WHERE empd.cust_no = %s
            """, (cust_no,))
            user_data['employer_details'] = cursor.fetchone()
        else:
            user_data['employer_details'] = None


        # Fetch Company Affiliations
        cursor.execute("SELECT * FROM company_affiliation WHERE cust_no = %s", (cust_no,))
        user_data['company_affiliations'] = cursor.fetchall()

        # Fetch Existing Bank Accounts
        cursor.execute("""
            SELECT eb.acc_type, bd.bank_name, bd.branch
            FROM existing_bank eb
            JOIN bank_details bd ON eb.bank_code = bd.bank_code
            WHERE eb.cust_no = %s
        """, (cust_no,))
        user_data['existing_banks'] = cursor.fetchall()

        # Fetch Public Official Relationships
        cursor.execute("""
            SELECT cpr.relation_desc, pod.gov_int_name, pod.official_position, pod.branch_orgname
            FROM cust_po_relationship cpr
            JOIN public_official_details pod ON cpr.gov_int_id = pod.gov_int_id
            WHERE cpr.cust_no = %s
        """, (cust_no,))
        user_data['public_official_relationships'] = cursor.fetchall()

        return render_template('userform.html', user_data=user_data)

    except mysql.connector.Error as err:
        print(f"Database error in userHome: {err}")
        flash(f'An error occurred while fetching your data: {err}', 'danger')
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Error in userHome: {e}")
        flash('An unexpected error occurred while loading your profile.', 'danger')
        return redirect(url_for('login'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---ROUTE: Logouts ---
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'info')
    response = redirect(url_for('login'))
    
    # Prevent back button from caching the page
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response



# ---ROUTE: Login User/Admin ---
# START OF MODIFICATIONS - PART 5: UPDATED login ROUTE

# ---ROUTE: Login User/Admin ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('username')
        password_input = request.form.get('password')

        # Admin login (keep separate if specific admin credentials are hardcoded)
        if email == 'admin@gmail.com' and password_input == 'LandBank@2025':
            session['admin'] = True
            session['user_email'] = email
            flash('Logged in as Admin successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if not conn:
                flash('Database connection failed.', 'danger')
                return render_template('login.html', error='Database connection failed.')

            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT credentials.cust_no, username, password, customer.custname
                FROM credentials
                JOIN customer ON credentials.cust_no = customer.cust_no
                WHERE username = %s
            """, (email,))
            user = cursor.fetchone()

            # Check if user exists and if the provided password matches the stored hash
            if user and check_password_hash(user['password'], password_input): # Use check_password_hash
                session['user'] = user['custname']
                session['user_email'] = user['username']
                session['cust_no'] = user['cust_no']

                flash('Logged in successfully!', 'success')
                return redirect(url_for('home')) # Redirect to user dashboard/home
            else:
                flash('Invalid username or password.', 'danger')
                return render_template('login.html', error='Invalid username or password.')

        except mysql.connector.Error as err:
            print(f"Database error during login: {err}")
            flash(f'An error occurred during login: {err}', 'danger')
            return render_template('login.html', error=f"Database error during login: {err}")
        except Exception as e:
            print(f"Login error: {e}")
            flash('An unexpected error occurred during login.', 'danger')
            return render_template('login.html', error='An unexpected error occurred during login.')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('login.html')

# END OF MODIFICATIONS - PART 5

@app.route('/registrationSuccess')
def registration_success():
    """Renders the registration success page."""
    return render_template('registrationSuccess.html')

# ---ROUTE: Admin Dashboard ---

@app.route('/admin_dashboard')
@no_cache
def admin_dashboard():
    if 'admin' not in session:
        flash('Please login to access the admin dashboard.', 'warning')
        return redirect(url_for('login'))
   

    conn = None
    cursor = None
    try:
        # Get search and filter parameters from the request
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        date_filter = request.args.get('date', '')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return render_template('login.html', error='Database connection failed.')

        cursor = conn.cursor(dictionary=True)
        
        # Base query
        query = """
            SELECT c.cust_no, c.custname, c.email_address, c.contact_no, c.status, c.datebirth
            FROM customer c
            WHERE 1=1
        """
        params = []

        # Add search conditions (cust_no, email_address, full name)
        if search_query:
            query += " AND (c.cust_no LIKE %s OR c.email_address LIKE %s OR c.custname LIKE %s)"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])

        # Add status filter (Active, Pending, Inactive)
        if status_filter:
            query += " AND c.status = %s"
            params.append(status_filter)

        # Add date filter (using datebirth field)
        if date_filter:
            query += " AND DATE(c.datebirth) = %s"
            params.append(date_filter)

        # Complete query with ordering
        query += " ORDER BY c.cust_no DESC"

        cursor.execute(query, params)
        customers = cursor.fetchall()

        return render_template('admin_dashboard.html', 
                            customers=customers,
                            current_search=search_query,
                            current_status=status_filter,
                            current_date=date_filter)

    except mysql.connector.Error as err:
        print(f"Database error in admin_dashboard: {err}")
        flash(f'An error occurred while fetching customer data: {err}', 'danger')
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Error in admin_dashboard: {e}")
        flash('An unexpected error occurred while loading the dashboard.', 'danger')
        return redirect(url_for('login'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- ROUTE: Admin View Customer Details ---
@app.route('/admin/customer/<string:cust_no>')
def admin_view_customer(cust_no):
    if 'admin' not in session:
        flash('Please login to access the admin dashboard.', 'warning')
        return redirect(url_for('login'))

    conn = None
    cursor = None
    user_data = {} # This dictionary will hold all fetched data

    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('admin_dashboard'))

        cursor = conn.cursor(dictionary=True) # Use dictionary=True for easy access by column name

        # Fetch Customer Information (main customer table joined with occupation and financial_record)
        cursor.execute("""
            SELECT c.*, o.occ_type, o.bus_nature, f.source_wealth, f.mon_income, f.ann_income
            FROM customer c
            LEFT JOIN occupation o ON c.occ_id = o.occ_id
            LEFT JOIN financial_record f ON c.fin_code = f.fin_code
            WHERE c.cust_no = %s
        """, (cust_no,))
        user_data['customer'] = cursor.fetchone()

        if not user_data['customer']:
            flash(f'Customer with ID {cust_no} not found.', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Separate the fetched data for clarity in the template
        # The .get() method is used to safely access keys, returning None if not found,
        # which helps prevent errors if a joined field is NULL.
        user_data['occupation'] = {
            'occ_type': user_data['customer'].get('occ_type'),
            'bus_nature': user_data['customer'].get('bus_nature')
        }
        user_data['financial_record'] = {
            'source_wealth': user_data['customer'].get('source_wealth'),
            'mon_income': user_data['customer'].get('mon_income'),
            'ann_income': user_data['customer'].get('ann_income')
        }

        # Fetch Spouse Information (if exists)
        cursor.execute("SELECT * FROM spouse WHERE cust_no = %s", (cust_no,))
        user_data['spouse'] = cursor.fetchone()

        # Fetch Employer Details (conditional on occupation type)
        if user_data['occupation']['occ_type'] == 'Employed':
            cursor.execute("""
                SELECT ed.*
                FROM employer_details ed
                JOIN employment_details empd ON ed.emp_id = empd.emp_id
                WHERE empd.cust_no = %s
            """, (cust_no,))
            user_data['employer_details'] = cursor.fetchone()
        else:
            user_data['employer_details'] = None

        # Fetch Company Affiliations (multiple records possible)
        cursor.execute("SELECT * FROM company_affiliation WHERE cust_no = %s", (cust_no,))
        user_data['company_affiliations'] = cursor.fetchall()

        # Fetch Existing Bank Accounts (multiple records possible)
        cursor.execute("""
            SELECT eb.acc_type, bd.bank_name, bd.branch
            FROM existing_bank eb
            JOIN bank_details bd ON eb.bank_code = bd.bank_code
            WHERE eb.cust_no = %s
        """, (cust_no,))
        user_data['existing_banks'] = cursor.fetchall()

        # Fetch Public Official Relationships (multiple records possible)
        cursor.execute("""
            SELECT cpr.relation_desc, pod.gov_int_name, pod.official_position, pod.branch_orgname
            FROM cust_po_relationship cpr
            JOIN public_official_details pod ON cpr.gov_int_id = pod.gov_int_id
            WHERE cpr.cust_no = %s
        """, (cust_no,))
        user_data['public_official_relationships'] = cursor.fetchall()

        # Render the template, passing all collected data in 'user_data'
        return render_template('admin_view_customer.html', user_data=user_data)

    except mysql.connector.Error as err:
        print(f"Database error in admin_view_customer: {err}")
        flash(f'An error occurred while fetching customer data: {err}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"Error in admin_view_customer: {e}")
        flash('An unexpected error occurred while loading customer details.', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---ROUTE: Admin Edit Customer Details ---
@app.route('/admin/edit_customer/<string:cust_no>', methods=['GET', 'POST'])
def admin_edit_customer(cust_no):
    if 'admin' not in session:
        flash('Please login to access the admin dashboard.', 'warning')
        return redirect(url_for('login'))

    conn = None
    cursor = None
    customer_data = {} # Will hold all fetched data for the customer

    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('admin_dashboard'))

        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            # --- Handle form submission for UPDATE ---
            conn.start_transaction()
            try:
                # Retrieve all form data
                # Customer Details
                custname = request.form.get('custname')
                email_address = request.form.get('email_address')
                contact_no = request.form.get('contact_no')
                datebirth = request.form.get('datebirth')
                nationality = request.form.get('nationality')
                citizenship = request.form.get('citizenship')
                custsex = request.form.get('custsex')
                placebirth = request.form.get('placebirth')
                civilstatus = request.form.get('civilstatus')
                num_children = int(request.form.get('num_children', 0) or 0)
                mmaiden_name = request.form.get('mmaiden_name')
                cust_address = request.form.get('cust_address')

                # Occupation Details
                occ_type = request.form.get('occ_type')
                bus_nature = request.form.get('bus_nature')

                # Financial Record Details
                source_wealth = request.form.get('source_wealth')
                mon_income = request.form.get('mon_income')
                ann_income = request.form.get('ann_income')

                # Spouse Details
                sp_name = request.form.get('sp_name')
                sp_datebirth = request.form.get('sp_datebirth')
                sp_profession = request.form.get('sp_profession')

                # Employer Details (if employed)
                tin_id = request.form.get('tin_id')
                empname = request.form.get('empname')
                emp_address = request.form.get('emp_address')
                phonefax_no = request.form.get('phonefax_no')
                job_title = request.form.get('job_title')
                emp_date = request.form.get('emp_date') or None # Use None for empty date string

                # Company Affiliations (multiple)
                depositor_roles = request.form.getlist('depositor_role[]')
                dep_compnames = request.form.getlist('dep_compname[]')

                # Existing Banks (multiple)
                bank_names = request.form.getlist('bank_name[]')
                branches = request.form.getlist('branch[]')
                acc_types = request.form.getlist('acc_type[]')

                # Public Official Relationships (multiple)
                gov_int_names = request.form.getlist('gov_int_name[]')
                official_positions = request.form.getlist('official_position[]')
                branch_orgnames = request.form.getlist('branch_orgname[]')
                relation_descs = request.form.getlist('relation_desc[]')


                # --- 1. Update Occupation and Financial Record tables first (or insert if new) ---
                # Fetch existing occ_id and fin_code for the customer
                cursor.execute("SELECT occ_id, fin_code FROM customer WHERE cust_no = %s", (cust_no,))
                current_codes = cursor.fetchone()
                current_occ_id = current_codes['occ_id'] if current_codes else None
                current_fin_code = current_codes['fin_code'] if current_codes else None

                # Update Occupation
                if current_occ_id:
                    sql_update_occ = """
                        UPDATE occupation SET occ_type = %s, bus_nature = %s WHERE occ_id = %s
                    """
                    cursor.execute(sql_update_occ, (occ_type, bus_nature, current_occ_id))
                else: # Should ideally not happen if customer already exists, but as a fallback
                    new_occ_id = str(uuid.uuid4())[:10].upper()
                    sql_insert_occ = "INSERT INTO occupation (occ_id, occ_type, bus_nature) VALUES (%s, %s, %s)"
                    cursor.execute(sql_insert_occ, (new_occ_id, occ_type, bus_nature))
                    current_occ_id = new_occ_id # Update occ_id to be used in customer table update

                # Update Financial Record
                if current_fin_code:
                    sql_update_fin = """
                        UPDATE financial_record SET source_wealth = %s, mon_income = %s, ann_income = %s WHERE fin_code = %s
                    """
                    cursor.execute(sql_update_fin, (source_wealth, mon_income, ann_income, current_fin_code))
                else: # Fallback for new financial record
                    new_fin_code = str(uuid.uuid4())[:10].upper()
                    sql_insert_fin = "INSERT INTO financial_record (fin_code, source_wealth, mon_income, ann_income) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql_insert_fin, (new_fin_code, source_wealth, mon_income, ann_income))
                    current_fin_code = new_fin_code # Update fin_code to be used in customer table update


                # --- 2. Update Customer table ---
                sql_update_customer = """
                    UPDATE customer SET
                        custname = %s, email_address = %s, contact_no = %s,
                        datebirth = %s, nationality = %s, citizenship = %s,
                        custsex = %s, placebirth = %s, civilstatus = %s,
                        num_children = %s, mmaiden_name = %s, cust_address = %s,
                        occ_id = %s, fin_code = %s
                    WHERE cust_no = %s
                """
                customer_update_data = (
                    custname, email_address, contact_no, datebirth, nationality,
                    citizenship, custsex, placebirth, civilstatus, num_children,
                    mmaiden_name, cust_address, current_occ_id, current_fin_code, cust_no
                )
                cursor.execute(sql_update_customer, customer_update_data)

                # --- 3. Update Spouse table ---
                if civilstatus == 'Married' and sp_name and sp_datebirth and sp_profession:
                    # Check if spouse record exists
                    cursor.execute("SELECT COUNT(*) FROM spouse WHERE cust_no = %s", (cust_no,))
                    if cursor.fetchone()[0] > 0:
                        sql_update_spouse = """
                            UPDATE spouse SET sp_name = %s, sp_datebirth = %s, sp_profession = %s
                            WHERE cust_no = %s
                        """
                        cursor.execute(sql_update_spouse, (sp_name, sp_datebirth, sp_profession, cust_no))
                    else:
                        sql_insert_spouse = """
                            INSERT INTO spouse (cust_no, sp_name, sp_datebirth, sp_profession)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(sql_insert_spouse, (cust_no, sp_name, sp_datebirth, sp_profession))
                else:
                    # If not married or data removed, delete spouse record
                    cursor.execute("DELETE FROM spouse WHERE cust_no = %s", (cust_no,))

                # --- 4. Update Employer Details and Employment Details ---
                if occ_type == 'Employed':
                    # Get existing emp_id if any
                    cursor.execute("SELECT emp_id FROM employment_details WHERE cust_no = %s", (cust_no,))
                    emp_link = cursor.fetchone()
                    existing_emp_id = emp_link['emp_id'] if emp_link else None

                    if existing_emp_id:
                        sql_update_employer = """
                            UPDATE employer_details SET
                                tin_id = %s, empname = %s, emp_address = %s,
                                phonefax_no = %s, job_title = %s, emp_date = %s
                            WHERE emp_id = %s
                        """
                        cursor.execute(sql_update_employer, (tin_id, empname, emp_address, phonefax_no, job_title, emp_date, existing_emp_id))
                    else:
                        # Insert new employer and link if none existed before
                        new_emp_id = str(uuid.uuid4())[:10].upper()
                        sql_insert_employer = """
                            INSERT INTO employer_details (emp_id, occ_id, tin_id, empname, emp_address, phonefax_no, job_title, emp_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql_insert_employer, (new_emp_id, current_occ_id, tin_id, empname, emp_address, phonefax_no, job_title, emp_date))
                        sql_insert_emp_link = "INSERT INTO employment_details (cust_no, emp_id) VALUES (%s, %s)"
                        cursor.execute(sql_insert_emp_link, (cust_no, new_emp_id))
                else:
                    # If no longer employed, delete employer and employment details
                    cursor.execute("SELECT emp_id FROM employment_details WHERE cust_no = %s", (cust_no,))
                    emp_link_to_delete = cursor.fetchone()
                    if emp_link_to_delete:
                        cursor.execute("DELETE FROM employment_details WHERE cust_no = %s", (cust_no,))
                        cursor.execute("DELETE FROM employer_details WHERE emp_id = %s", (emp_link_to_delete['emp_id'],))


                # --- 5. Update Company Affiliations (delete all existing, then re-insert) ---
                cursor.execute("DELETE FROM company_affiliation WHERE cust_no = %s", (cust_no,))
                for i in range(len(depositor_roles)):
                    if depositor_roles[i] and dep_compnames[i]:
                        sql_insert_comp_aff = "INSERT INTO company_affiliation (cust_no, depositor_role, dep_compname) VALUES (%s, %s, %s)"
                        cursor.execute(sql_insert_comp_aff, (cust_no, depositor_roles[i], dep_compnames[i]))

                # --- 6. Update Existing Banks (delete all existing, then re-insert) ---
                cursor.execute("DELETE FROM existing_bank WHERE cust_no = %s", (cust_no,))
                # Also delete bank_details if no other customer uses it (optional, for cleanup)
                # This requires more complex logic to check for references before deleting from bank_details
                # For simplicity here, we'll only delete from existing_bank.
                for i in range(len(bank_names)):
                    if bank_names[i] and branches[i] and acc_types[i]:
                        # Ensure bank_details exists or insert it
                        sql_insert_bank_details = "INSERT IGNORE INTO bank_details (bank_code, bank_name, branch) VALUES (%s, %s, %s)"
                        cursor.execute(sql_insert_bank_details, (bank_names[i], bank_names[i], branches[i])) # Assuming bank_name can be bank_code for simplicity

                        sql_insert_existing_bank = "INSERT INTO existing_bank (cust_no, bank_code, acc_type) VALUES (%s, %s, %s)"
                        cursor.execute(sql_insert_existing_bank, (cust_no, bank_names[i], acc_types[i]))

                # --- 7. Update Public Official Relationships (delete all existing, then re-insert) ---
                # Similar to company affiliations, delete all existing and re-insert
                cursor.execute("DELETE FROM cust_po_relationship WHERE cust_no = %s", (cust_no,))
                # Also consider deleting from public_official_details if no other customer refers to them
                # This is more complex and might involve checking counts of references before deletion.
                for i in range(len(gov_int_names)):
                    if gov_int_names[i] and official_positions[i] and branch_orgnames[i] and relation_descs[i]:
                        # Check if public official already exists by name/position/org
                        sql_check_po = "SELECT gov_int_id FROM public_official_details WHERE gov_int_name = %s AND official_position = %s AND branch_orgname = %s"
                        cursor.execute(sql_check_po, (gov_int_names[i], official_positions[i], branch_orgnames[i]))
                        po_id_result = cursor.fetchone()
                        
                        po_id = None
                        if po_id_result:
                            po_id = po_id_result['gov_int_id']
                        else:
                            # Insert new public official if not found
                            po_id = str(uuid.uuid4())[:10].upper()
                            sql_insert_po = "INSERT INTO public_official_details (gov_int_id, gov_int_name, official_position, branch_orgname) VALUES (%s, %s, %s, %s)"
                            cursor.execute(sql_insert_po, (po_id, gov_int_names[i], official_positions[i], branch_orgnames[i]))

                        sql_insert_po_rel = "INSERT INTO cust_po_relationship (cust_no, gov_int_id, relation_desc) VALUES (%s, %s, %s)"
                        cursor.execute(sql_insert_po_rel, (cust_no, po_id, relation_descs[i]))

                conn.commit()
                flash('Customer details updated successfully!', 'success')
                return redirect(url_for('admin_view_customer', cust_no=cust_no))

            except mysql.connector.Error as err:
                conn.rollback()
                print(f"Database error during customer update: {err}")
                flash(f'An error occurred during customer update: {err}', 'danger')
                return redirect(url_for('admin_edit_customer', cust_no=cust_no))
            except Exception as e:
                conn.rollback()
                print(f"Unexpected error during customer update: {e}")
                flash(f'An unexpected error occurred: {e}', 'danger')
                return redirect(url_for('admin_edit_customer', cust_no=cust_no))


        # --- Handle GET request (and fall-through from POST on error) for displaying current data ---
        # Fetch Customer Information
        cursor.execute("""
            SELECT c.*, o.occ_type, o.bus_nature, f.source_wealth, f.mon_income, f.ann_income
            FROM customer c
            LEFT JOIN occupation o ON c.occ_id = o.occ_id
            LEFT JOIN financial_record f ON c.fin_code = f.fin_code
            WHERE c.cust_no = %s
        """, (cust_no,))
        customer_data['customer'] = cursor.fetchone()

        if not customer_data['customer']:
            flash(f'Customer with ID {cust_no} not found.', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Separate the fetched data for clarity in the template
        # Make sure these keys exist, even if None
        customer_data['occupation'] = {
            'occ_type': customer_data['customer'].get('occ_type'),
            'bus_nature': customer_data['customer'].get('bus_nature')
        }
        customer_data['financial_record'] = {
            'source_wealth': customer_data['customer'].get('source_wealth'),
            'mon_income': customer_data['customer'].get('mon_income'),
            'ann_income': customer_data['customer'].get('ann_income')
        }

        # Fetch Spouse Information (if exists)
        cursor.execute("SELECT * FROM spouse WHERE cust_no = %s", (cust_no,))
        customer_data['spouse'] = cursor.fetchone()

        # Fetch Employer Details (if exists and occupation is 'Employed')
        if customer_data['occupation']['occ_type'] == 'Employed':
            cursor.execute("""
                SELECT ed.*
                FROM employer_details ed
                JOIN employment_details empd ON ed.emp_id = empd.emp_id
                WHERE empd.cust_no = %s
            """, (cust_no,))
            customer_data['employer_details'] = cursor.fetchone()
        else:
            customer_data['employer_details'] = None

        # Fetch Company Affiliations
        cursor.execute("SELECT * FROM company_affiliation WHERE cust_no = %s", (cust_no,))
        customer_data['company_affiliations'] = cursor.fetchall()

        # Fetch Existing Bank Accounts
        cursor.execute("""
            SELECT eb.acc_type, bd.bank_name, bd.branch
            FROM existing_bank eb
            JOIN bank_details bd ON eb.bank_code = bd.bank_code
            WHERE eb.cust_no = %s
        """, (cust_no,))
        customer_data['existing_banks'] = cursor.fetchall()

        # Fetch Public Official Relationships
        cursor.execute("""
            SELECT cpr.relation_desc, pod.gov_int_name, pod.official_position, pod.branch_orgname
            FROM cust_po_relationship cpr
            JOIN public_official_details pod ON cpr.gov_int_id = pod.gov_int_id
            WHERE cpr.cust_no = %s
        """, (cust_no,))
        customer_data['public_official_relationships'] = cursor.fetchall()

        return render_template('admin_edit_customer.html', customer_data=customer_data)

    except mysql.connector.Error as err:
        print(f"Database error in admin_edit_customer (GET/initial load): {err}")
        flash(f'An error occurred while fetching customer data: {err}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"Error in admin_edit_customer (GET/initial load): {e}")
        flash('An unexpected error occurred while loading customer details for editing.', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --- ROUTE: dmin add customer ---
@app.route('/admin_add_customer', methods=['POST'])
def admin_add_customer():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('admin_dashboard'))

        cursor = conn.cursor()
        conn.start_transaction()

        # --- Generate Customer ID ---
        cust_no = str(uuid.uuid4())[:10].upper()

        # --- Personal Info ---
        custname = f"{request.form['firstName']} {request.form['lastName']}"
        datebirth = request.form['datebirth']
        nationality = request.form['nationality']
        citizenship = request.form['citizenship']
        custsex = request.form['custsex']
        placebirth = request.form['placebirth']
        civilstatus = request.form['civilstatus']
        num_children = int(request.form.get('num_children', 0) or 0)
        mmaiden_name = request.form['mmaiden_name']
        cust_address = request.form['cust_address']
        email_address = request.form['email_address']
        contact_no = request.form['contact_no']
        status = request.form.get('status', 'Active')

        # --- Occupation Info ---
        occ_id = str(uuid.uuid4())[:10].upper()
        occ_type = request.form['occupation']
        bus_nature = request.form['natureOfBusiness']

        # Insert into occupation table
        cursor.execute("""
            INSERT INTO occupation (occ_id, occ_type, bus_nature)
            VALUES (%s, %s, %s)
        """, (occ_id, occ_type, bus_nature))

        # --- Financial Info ---
        fin_code = str(uuid.uuid4())[:10].upper()
        source_wealth = ', '.join(request.form.getlist('source_wealth[]'))
        mon_income = request.form['monthly_income']
        ann_income = request.form['annual_income']

        # Insert into financial_record table
        cursor.execute("""
            INSERT INTO financial_record (fin_code, source_wealth, mon_income, ann_income)
            VALUES (%s, %s, %s, %s)
        """, (fin_code, source_wealth, mon_income, ann_income))

        # --- Insert Customer ---
        cursor.execute("""
            INSERT INTO customer (
                cust_no, custname, datebirth, nationality, citizenship, custsex,
                placebirth, civilstatus, num_children, mmaiden_name, cust_address,
                email_address, contact_no, occ_id, fin_code, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            cust_no, custname, datebirth, nationality, citizenship, custsex,
            placebirth, civilstatus, num_children, mmaiden_name, cust_address,
            email_address, contact_no, occ_id, fin_code, status
        ))

        # --- Spouse Info ---
        if civilstatus == 'Married':
            sp_name = f"{request.form.get('spouseFirstName', '')} {request.form.get('spouseLastName', '')}".strip()
            sp_datebirth = request.form.get('spouseDob')
            sp_profession = request.form.get('spouseProfession')
            
            if sp_name and sp_datebirth and sp_profession:
                cursor.execute("""
                    INSERT INTO spouse (cust_no, sp_name, sp_datebirth, sp_profession)
                    VALUES (%s, %s, %s, %s)
                """, (cust_no, sp_name, sp_datebirth, sp_profession))

        # --- Employer Info ---
        if occ_type == 'Employed':
            emp_id = str(uuid.uuid4())[:10].upper()
            tin_id = request.form.get('tin_id', '')
            empname = request.form.get('empname', '')
            emp_address = request.form.get('emp_address', '')
            phonefax_no = request.form.get('phonefax_no', '')
            job_title = request.form.get('job_title', '')
            emp_date = request.form.get('emp_date') or '2000-01-01'

            cursor.execute("""
                INSERT INTO employer_details (
                    emp_id, occ_id, tin_id, empname, emp_address, phonefax_no, job_title, emp_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (emp_id, occ_id, tin_id, empname, emp_address, phonefax_no, job_title, emp_date))

            cursor.execute("""
                INSERT INTO employment_details (cust_no, emp_id)
                VALUES (%s, %s)
            """, (cust_no, emp_id))

        # --- Company Affiliations ---
        depositor_roles = request.form.getlist('depositorRole[]')
        dep_compnames = request.form.getlist('dep_compname[]')
        
        for role, company in zip(depositor_roles, dep_compnames):
            if role and company:
                cursor.execute("""
                    INSERT INTO company_affiliation (cust_no, depositor_role, dep_compname)
                    VALUES (%s, %s, %s)
                """, (cust_no, role, company))

        # --- Existing Bank Accounts ---
        bank_names = request.form.getlist('bank_name[]')
        branches = request.form.getlist('branch[]')
        acc_types = request.form.getlist('acc_type[]')
        
        for bank_name, branch, acc_type in zip(bank_names, branches, acc_types):
            if bank_name and branch and acc_type:
                # First ensure bank exists
                bank_code = str(uuid.uuid4())[:10].upper()
                cursor.execute("""
                    INSERT IGNORE INTO bank_details (bank_code, bank_name, branch)
                    VALUES (%s, %s, %s)
                """, (bank_code, bank_name, branch))
                
                cursor.execute("""
                    INSERT INTO existing_bank (cust_no, bank_code, acc_type)
                    VALUES (%s, %s, %s)
                """, (cust_no, bank_code, acc_type))

        # --- Public Official Relationships ---
        gov_last_names = request.form.getlist('govLastName[]')
        gov_first_names = request.form.getlist('govFirstName[]')
        gov_middle_names = request.form.getlist('govMiddleName[]')
        relations = request.form.getlist('relationship[]')
        positions = request.form.getlist('position[]')
        org_names = request.form.getlist('govBranchOrgName[]')
        
        for lname, fname, mname, relation, pos, org in zip(
            gov_last_names, gov_first_names, gov_middle_names, 
            relations, positions, org_names
        ):
            if fname and lname and relation and pos and org:
                gov_int_id = str(uuid.uuid4())[:10].upper()
                gov_int_name = f"{fname} {mname} {lname}".strip()
                
                cursor.execute("""
                    INSERT INTO public_official_details (
                        gov_int_id, gov_int_name, official_position, branch_orgname
                    ) VALUES (%s, %s, %s, %s)
                """, (gov_int_id, gov_int_name, pos, org))
                
                cursor.execute("""
                    INSERT INTO cust_po_relationship (cust_no, gov_int_id, relation_desc)
                    VALUES (%s, %s, %s)
                """, (cust_no, gov_int_id, relation))

        # --- Insert Credentials ---
        username = email_address
        password = f"defaultPass{cust_no}"  # In production, use proper password hashing
        
        cursor.execute("""
            INSERT INTO credentials (cust_no, username, password)
            VALUES (%s, %s, %s)
        """, (cust_no, username, password))

        conn.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        flash(f'Database error: {err}', 'danger')
        print(f"Database error during customer addition: {err}")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        print(f"Error during customer addition: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('admin_dashboard'))



# --- ROUTE: Delete Customer ---
@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    if 'admin' not in session:
        flash('Please login to access this function.', 'warning')
        return redirect(url_for('login'))

    cust_no = request.form.get('cust_no')
    if not cust_no:
        flash('Customer ID is missing for deletion.', 'danger')
        return redirect(url_for('admin_dashboard'))

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('admin_dashboard'))

        cursor = conn.cursor()

        # Start a transaction to ensure data integrity
        conn.start_transaction()

        # Delete from tables that have foreign keys referencing customer (or other tables that reference others)
        # Order of deletion is crucial due to foreign key constraints:
        # Delete child records first, then parent records.

        # ADDED: Delete from credentials table first
        cursor.execute("DELETE FROM credentials WHERE cust_no = %s", (cust_no,))

        # 1. Delete from cust_po_relationship
        cursor.execute("DELETE FROM cust_po_relationship WHERE cust_no = %s", (cust_no,))

        # 2. Delete from existing_bank
        cursor.execute("DELETE FROM existing_bank WHERE cust_no = %s", (cust_no,))

        # 3. Delete from company_affiliation
        cursor.execute("DELETE FROM company_affiliation WHERE cust_no = %s", (cust_no,))

        # 4. Handle employment_details and employer_details
        # First, find emp_id from employment_details if customer is employed
        cursor.execute("SELECT emp_id FROM employment_details WHERE cust_no = %s", (cust_no,))
        emp_id_result = cursor.fetchone()
        emp_id = emp_id_result[0] if emp_id_result else None

        # Delete from employment_details
        cursor.execute("DELETE FROM employment_details WHERE cust_no = %s", (cust_no,))

        # If emp_id exists, delete from employer_details (assuming emp_id is unique to employment_details)
        if emp_id:
            cursor.execute("DELETE FROM employer_details WHERE emp_id = %s", (emp_id,))
            
        # 5. Delete from spouse
        cursor.execute("DELETE FROM spouse WHERE cust_no = %s", (cust_no,))

        # 6. Get fin_code and occ_id before deleting from customer
        cursor.execute("SELECT fin_code, occ_id FROM customer WHERE cust_no = %s", (cust_no,))
        customer_info = cursor.fetchone()
        fin_code = customer_info[0] if customer_info else None
        occ_id = customer_info[1] if customer_info else None

        # 7. Finally, delete from customer
        cursor.execute("DELETE FROM customer WHERE cust_no = %s", (cust_no,))

        # 8. Delete from financial_record if fin_code exists and is no longer referenced by other customers
        if fin_code:
            cursor.execute("SELECT COUNT(*) FROM customer WHERE fin_code = %s", (fin_code,))
            if cursor.fetchone()[0] == 0: # If no other customers use this fin_code
                cursor.execute("DELETE FROM financial_record WHERE fin_code = %s", (fin_code,))
        
        # 9. Delete from occupation if occ_id exists and is no longer referenced by other customers
        if occ_id:
            cursor.execute("SELECT COUNT(*) FROM customer WHERE occ_id = %s", (occ_id,))
            if cursor.fetchone()[0] == 0: # If no other customers use this occ_id
                cursor.execute("DELETE FROM occupation WHERE occ_id = %s", (occ_id,))


        conn.commit() # Commit the transaction if all deletions are successful
        flash(f'Customer {cust_no} and all related records deleted successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    except mysql.connector.Error as err:
        conn.rollback() # Rollback on error
        print(f"Database error during customer deletion: {err}")
        flash(f'An error occurred during deletion: {err}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        if conn: # Check if conn exists before trying to rollback
            conn.rollback()
        print(f"Error during customer deletion: {e}")
        flash('An unexpected error occurred during customer deletion.', 'danger')
        return redirect(url_for('admin_dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


UPLOAD_FOLDER = 'static/uploads'  # You can change this
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        flash('No file part', 'error')
        return redirect(request.referrer)

    file = request.files['photo']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.referrer)

    if file and allowed_file(file.filename):
        # Overwrite the default user icon
        save_path = os.path.join('static', 'assets', 'user-icon.png')
        file.save(save_path)
        flash('Profile photo uploaded successfully!', 'success')
        return redirect(request.referrer)
    else:
        flash('Invalid file type', 'error')
        return redirect(request.referrer)
    
# START OF MODIFICATIONS - PART 4: UPDATED r1 ROUTE

# --- ROUTE: Register Customer Step 1 ---
@app.route('/r1', methods=['GET', 'POST'])
def r1():
    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if not conn:
                flash('Database connection failed.', 'danger')
                return render_template('r1.html', error='Database connection failed.')

            cursor = conn.cursor(dictionary=True)

            # Generate the new cust_no
            cust_no = generate_next_cust_no(cursor)
            if not cust_no:
                flash('Failed to generate customer number. Please try again.', 'danger')
                return render_template('r1.html')

            # Extract form data
            data = {
                'cust_no': cust_no, # Use the generated cust_no
                'custname': request.form['custname'],
                'datebirth': request.form['datebirth'],
                'nationality': request.form['nationality'],
                'citizenship': request.form['citizenship'],
                'custsex': request.form['custsex'],
                'placebirth': request.form['placebirth'],
                'civilstatus': request.form['civilstatus'],
                'num_children': int(request.form['num_children']),
                'mmaiden_name': request.form['mmaiden_name'],
                'cust_address': request.form['cust_address'],
                'email_address': request.form['email_address'],
                'contact_no': request.form['contact_no'],
                'occ_type': request.form['occ_type'], # From form for occupation
                'bus_nature': request.form['bus_nature'], # From form for occupation
                'source_wealth': request.form['source_wealth'], # From form for financial
                'mon_income': request.form['mon_income'], # From form for financial
                'ann_income': request.form['ann_income'], # From form for financial
                'password': request.form.get('password', 'default_password_for_new_user') # Get password from form or use default
            }

            # Get or insert occupation and financial record, ensuring unique IDs
            occ_id = get_or_insert_occupation(cursor, data['occ_type'], data['bus_nature'])
            fin_code = get_or_insert_financial_record(cursor, data['source_wealth'], data['mon_income'], data['ann_income'])

            if not occ_id or not fin_code:
                flash('Error processing occupation or financial data. Please check inputs.', 'danger')
                conn.rollback() # Rollback if related data insertion fails
                return render_template('r1.html')

            # Insert into customer table
            sql_customer = """
                INSERT INTO customer (
                    cust_no, custname, datebirth, nationality, citizenship, custsex, placebirth,
                    civilstatus, num_children, mmaiden_name, cust_address, email_address,
                    contact_no, occ_id, fin_code, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Active')
            """
            cursor.execute(sql_customer, (
                data['cust_no'], data['custname'], data['datebirth'], data['nationality'],
                data['citizenship'], data['custsex'], data['placebirth'], data['civilstatus'],
                data['num_children'], data['mmaiden_name'], data['cust_address'],
                data['email_address'], data['contact_no'], occ_id, fin_code
            ))

            # Insert into credentials table using the generated cust_no and hashed password
            insert_credentials(cursor, data['cust_no'], {'email': data['email_address'], 'password': data['password']})

            conn.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login')) # Redirect to login page

        except mysql.connector.Error as err:
            if conn:
                conn.rollback() # Rollback changes if an error occurs
            print(f"Database error during registration: {err}")
            flash(f'An error occurred during registration: {err}', 'danger')
            return render_template('r1.html', error=f"Database error during registration: {err}")
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Registration error: {e}")
            flash('An unexpected error occurred during registration.', 'danger')
            return render_template('r1.html', error='An unexpected error occurred during registration.')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('r1.html')

# END OF MODIFICATIONS - PART 4



# --- Main execution block ---
if __name__ == '__main__':
    _ensure_database_schema() # Run schema check/update on app startup (for development)
    app.run(host='0.0.0.0', port=0000, debug=True) # Corrected port to 5000