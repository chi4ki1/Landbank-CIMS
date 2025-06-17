# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector # Import mysql.connector

# Create a Flask app instance
app = Flask(__name__)
# IMPORTANT: Change this secret key in production! It's used for session security.
app.secret_key = 'your_strong_secret_key_here_for_production'

# Database configuration
db_config = {
    'host': '127.0.0.1', # Use 127.0.0.1 for local MySQL, or your database host
    'port': '3306',
    'user': 'root',
    'password': 'LandBank@2025', # Your MySQL root password
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
    Ensures that necessary database columns have appropriate lengths.
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
        print("Attempting to ensure database schema (column lengths)...")

        # Increase length for relation_desc in cust_po_relationship
        try:
            cursor.execute("ALTER TABLE cust_po_relationship MODIFY COLUMN relation_desc VARCHAR(255);")
            print("Successfully altered 'relation_desc' column.")
        except mysql.connector.Error as err:
            # Error Code 1060: Duplicate column name (or already exists with same type)
            if err.errno == 1060 or "Duplicate column name" in str(err) or "Can't create table" in str(err) or "already exists" in str(err):
                 print(f"Column 'relation_desc' likely already exists or schema is already updated: {err}")
            else:
                print(f"Error altering 'relation_desc' column: {err}")
                conn.rollback() # Rollback any partial changes if an error occurs
                return # Exit if a critical error occurred

        # Increase length for mon_income and ann_income in financial_record
        try:
            cursor.execute("ALTER TABLE financial_record MODIFY COLUMN mon_income VARCHAR(255);")
            print("Successfully altered 'mon_income' column.")
        except mysql.connector.Error as err:
            if err.errno == 1060 or "Duplicate column name" in str(err) or "Can't create table" in str(err) or "already exists" in str(err):
                 print(f"Column 'mon_income' likely already exists or schema is already updated: {err}")
            else:
                print(f"Error altering 'mon_income' column: {err}")
                conn.rollback()
                return

        try:
            cursor.execute("ALTER TABLE financial_record MODIFY COLUMN ann_income VARCHAR(255);")
            print("Successfully altered 'ann_income' column.")
        except mysql.connector.Error as err:
            if err.errno == 1060 or "Duplicate column name" in str(err) or "Can't create table" in str(err) or "already exists" in str(err):
                 print(f"Column 'ann_income' likely already exists or schema is already updated: {err}")
            else:
                print(f"Error altering 'ann_income' column: {err}")
                conn.rollback()
                return

        conn.commit()
        print("Database schema update attempt finished.")

    except Exception as e:
        print(f"An unexpected error occurred during schema update: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --- Page Routes ---
@app.route('/')
def landing():
    """Renders the landing page."""
    return render_template('landing.html')

@app.route('/home')
def home():
    """Renders the home page."""
    return render_template('home.html')

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html')

@app.route('/services')
def services():
    """Renders the services page."""
    return render_template('services.html')

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template('contact.html')

@app.route('/registrationPrint')
def registrationPrint():
    """Renders the registration print/summary page."""
    return render_template('registrationPrint.html')

@app.route('/register')
def register():
    """Renders the registration page (initial entry point)."""
    return render_template('register.html')

# --- Registration Flow Pages (GET requests only, data handled by JS) ---
# These routes are now strictly GET to render HTML templates.
# Data collection and navigation logic is managed by registration.js on the client-side,
# and then submitted all at once to /submitRegistration.
@app.route('/registration1', methods=['GET'])
def registration1():
    """Renders the first step of the registration form."""
    return render_template('registration1.html')

@app.route('/registration2', methods=['GET'])
def registration2():
    """Renders the second step of the registration form."""
    return render_template('registration2.html')

@app.route('/registration3', methods=['GET'])
def registration3():
    """Renders the third step of the registration form."""
    return render_template('registration3.html')


@app.route('/submitRegistration', methods=['POST'])
def submit_registration():
    """
    Receives all registration data as JSON from the frontend (registration.js)
    and handles the complete database insertion, including credentials.
    """
    conn = None
    cursor = None
    try:
        # Get JSON data sent from the frontend
        data = request.get_json()
        r1 = data.get('registration1', {}) # Data from step 1
        r2 = data.get('registration2', {}) # Data from step 2
        r3 = data.get('registration3', {}) # Data from step 3

        conn = get_db_connection() # Use the consistent connection function
        if not conn:
            raise Exception("Database connection failed")
        
        cursor = conn.cursor()
        conn.start_transaction() # Start a transaction for atomicity

        # --- 1. Insert into occupation table ---
        occ_type = r2.get('occupation')
        bus_nature = r2.get('natureOfBusiness')
        sql_occ = "INSERT INTO occupation (occ_type, bus_nature) VALUES (%s, %s)"
        cursor.execute(sql_occ, (occ_type, bus_nature))
        occ_id = cursor.lastrowid

        # --- 2. Insert into financial_record table ---
        # Handle sourceOfWealth, which can be a list if multiple checkboxes selected
        source_wealth_list = r2.get('sourceOfWealth', [])
        source_wealth = ', '.join(source_wealth_list) if isinstance(source_wealth_list, list) else source_wealth_list
        
        mon_income = r2.get('monthlyIncome')
        ann_income = r2.get('annualIncome')
        sql_fin = "INSERT INTO financial_record (source_wealth, mon_income, ann_income) VALUES (%s, %s, %s)"
        cursor.execute(sql_fin, (source_wealth, mon_income, ann_income))
        fin_code = cursor.lastrowid

        # --- 3. Insert into customer table ---
        custname = f"{r1.get('firstName', '')} {r1.get('lastName', '')}"
        sql_cust = """INSERT INTO customer (custname, datebirth, nationality, citizenship, custsex, placebirth, civilstatus, num_children, mmaiden_name, cust_address, email_address, contact_no, occ_id, fin_code)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        customer_data = (
            custname, r1.get('dob'), r1.get('nationality'), r1.get('citizenship'),
            r1.get('sex'), r1.get('placeOfBirth'), r1.get('civilStatus'),
            int(r1.get('children', 0) or 0), # Ensure num_children is int, handle empty string to 0
            r1.get('motherMaidenName'), r1.get('address'),
            r1.get('email'), r1.get('telephone'), occ_id, fin_code
        )
        cursor.execute(sql_cust, customer_data)
        cust_no = cursor.lastrowid # Get the newly generated customer ID from AUTO_INCREMENT

        # --- 4. Insert into employer_details and employment_details if applicable ---
        if occ_type == 'Employed':
            tin_id = r2.get('tinId', '')
            empname = r2.get('companyName', '')
            emp_address = r2.get('employerAddress', '')
            phonefax_no = r2.get('employerPhone', '')
            job_title = r2.get('jobTitle', '')
            emp_date = r2.get('employmentDate', '2000-01-01') # Default date if not provided

            sql_emp_details = "INSERT INTO employer_details (tin_id, empname, emp_address, phonefax_no, job_title, emp_date) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_emp_details, (tin_id, empname, emp_address, phonefax_no, job_title, emp_date))
            emp_id = cursor.lastrowid

            sql_emp_link = "INSERT INTO employment_details (cust_no, emp_id) VALUES (%s, %s)"
            cursor.execute(sql_emp_link, (cust_no, emp_id))

        # --- 5. Insert into spouse table if married ---
        if r1.get('civilStatus') == 'Married' and r1.get('spouseFirstName'):
            sp_name = f"{r1.get('spouseFirstName', '')} {r1.get('spouseLastName', '')}"
            sp_datebirth = r1.get('spouseDob')
            sp_profession = r1.get('spouseProfession')
            sql_spouse = "INSERT INTO spouse (cust_no, sp_name, sp_datebirth, sp_profession) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_spouse, (cust_no, sp_name, sp_datebirth, sp_profession))

        # --- 6. Insert into company_affiliation ---
        roles = r3.get('depositorRole', [])
        companies = r3.get('companyName', [])
        # Ensure these are lists to prevent errors in zip
        if not isinstance(roles, list): roles = [roles] if roles else []
        if not isinstance(companies, list): companies = [companies] if companies else []

        for role, company in zip(roles, companies):
            if role and company: # Only insert if both role and company are provided
                sql_comp_aff = "INSERT INTO company_affiliation (cust_no, depositor_role, dep_compname) VALUES (%s, %s, %s)"
                cursor.execute(sql_comp_aff, (cust_no, role, company))

        # --- 7. Insert into bank_details and existing_bank ---
        banks = r3.get('bank', [])
        branches = r3.get('branch', [])
        acc_types = r3.get('accountType', [])
        # Ensure these are lists to prevent errors in zip
        if not isinstance(banks, list): banks = [banks] if banks else []
        if not isinstance(branches, list): branches = [branches] if branches else []
        if not isinstance(acc_types, list): acc_types = [acc_types] if acc_types else []

        for bank_name, branch, acc_type in zip(banks, branches, acc_types):
            if bank_name and branch and acc_type: # Only insert if all fields are provided
                # Use INSERT IGNORE to prevent errors if bank_details already exists
                sql_insert_bank = "INSERT IGNORE INTO bank_details (bank_code, bank_name, branch) VALUES (%s, %s, %s)"
                # Using bank_name as bank_code for simplicity. In a real app, bank_code might be separate.
                cursor.execute(sql_insert_bank, (bank_name, bank_name, branch)) 
                
                sql_existing_bank = "INSERT INTO existing_bank (cust_no, bank_code, acc_type) VALUES (%s, %s, %s)"
                cursor.execute(sql_existing_bank, (cust_no, bank_name, acc_type)) # bank_name used as bank_code

        # --- 8. Insert into public_official_details and cust_po_relationship ---
        gov_last_names = r3.get('govLastName', [])
        gov_first_names = r3.get('govFirstName', [])
        relationships = r3.get('relationship', [])
        positions = r3.get('position', [])
        org_names = r3.get('govBranchOrgName', [])
        
        # Ensure these are lists to prevent errors in loop
        if not isinstance(gov_last_names, list): gov_last_names = [gov_last_names] if gov_last_names else []
        if not isinstance(gov_first_names, list): gov_first_names = [gov_first_names] if gov_first_names else []
        if not isinstance(relationships, list): relationships = [relationships] if relationships else []
        if not isinstance(positions, list): positions = [positions] if positions else []
        if not isinstance(org_names, list): org_names = [org_names] if org_names else []

        # Iterate using the shortest list length to avoid index errors if lists are mismatched
        min_len = min(len(gov_last_names), len(gov_first_names), len(relationships), len(positions), len(org_names))
        for i in range(min_len):
            # Only insert if all related fields are present for a valid entry
            if gov_last_names[i] and gov_first_names[i] and relationships[i] and positions[i] and org_names[i]:
                gov_name = f"{gov_first_names[i]} {gov_last_names[i]}"
                sql_po_details = "INSERT INTO public_official_details (gov_int_name, official_position, branch_orgname) VALUES (%s, %s, %s)"
                cursor.execute(sql_po_details, (gov_name, positions[i], org_names[i]))
                gov_int_id = cursor.lastrowid

                sql_po_rel = "INSERT INTO cust_po_relationship (cust_no, gov_int_id, relation_desc) VALUES (%s, %s, %s)"
                cursor.execute(sql_po_rel, (cust_no, gov_int_id, relationships[i]))

        # --- 9. NEW: Call insert_credentials here to save username and password ---
        insert_credentials(cursor, cust_no, r1) # r1 contains the 'email' for username

        conn.commit() # Commit the transaction if all insertions are successful
        return '', 200 # Return success status (HTTP 200 OK)

    except mysql.connector.Error as err:
        if conn:
            conn.rollback() # Rollback on database error to ensure data consistency
        print(f"Error during registration submission: {err}")
        # Return a more informative error to the frontend for debugging
        return f"Database error during submission: {err}", 500 
    except Exception as e:
        if conn:
            conn.rollback() # Rollback on unexpected error
        print(f"Unexpected error during registration submission: {e}")
        return f"An unexpected error occurred: {e}", 500 
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Helper Function Definitions (Called from submit_registration) ---
def insert_credentials(cursor, cust_no, data):
    """
    Inserts user credentials (username and generated password) into the credentials table.
    """
    username = data.get('email')
    # Generate password based on user's request (e.g., 'defaultPass' + cust_no)
    # IMPORTANT: In a real application, you MUST hash passwords using a strong library (e.g., bcrypt).
    password = f"defaultPass{cust_no}" 

    sql = """
        INSERT INTO credentials (cust_no, username, password)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (cust_no, username, password))


@app.route('/registrationSuccess')
def registration_success():
    """Renders the registration success page."""
    return render_template('registrationSuccess.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('username')
        password_input = request.form.get('password')

        # --- Admin login check ---
        if email == 'admin@gmail.com' and password_input == 'LandBank@2025':
            session['admin'] = True
            session['user_email'] = email
            return redirect('/admin_dashboard')

        # --- Regular user login check ---
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if not conn:
                return render_template('login.html', error='Database connection failed.')

            cursor = conn.cursor(dictionary=True) # Use dictionary=True for easy column access

            # Query credentials table to find user and join with customer to get name
            cursor.execute("""
                SELECT credentials.cust_no, username, password, customer.custname
                FROM credentials
                JOIN customer ON credentials.cust_no = customer.cust_no
                WHERE username = %s
            """, (email,))
            user = cursor.fetchone()

            # Verify password (IMPORTANT: In production, compare hashed passwords)
            if user and user['password'] == password_input: # Current comparison is plain text as per password generation
                session['user'] = user['custname']
                session['user_email'] = user['username']
                session['cust_no'] = user['cust_no']
                
                # Redirect to userHome.html upon successful login
                return redirect('/userHome') 
            else:
                return render_template('login.html', error='Invalid email or password.')

        except mysql.connector.Error as db_err:
            print(f"Login DB Error: {db_err}")
            return render_template('login.html', error='Database error during login.')

        except Exception as e:
            print(f"Unexpected login error: {e}")
            return render_template('login.html', error='An unexpected error occurred during login.')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Render login page for GET request
    return render_template('login.html')

@app.route('/userHome')
def userHome():
    """
    Renders the user's home dashboard, displaying their account details.
    Fetches comprehensive user data from various linked tables.
    """
    if 'user' not in session or 'cust_no' not in session:
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))

    cust_no = session['cust_no']
    user_data = {}
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Database connection failed")
        
        cursor = conn.cursor(dictionary=True) # Use dictionary=True for easier data access by column name

        # Fetch Customer details
        cursor.execute("SELECT * FROM customer WHERE cust_no = %s", (cust_no,))
        user_data['customer'] = cursor.fetchone()
        if not user_data['customer']:
            # Customer not found, clear session and redirect to login
            session.clear()
            return redirect(url_for('login'))

        # Fetch Occupation details
        occ_id = user_data['customer'].get('occ_id')
        if occ_id:
            cursor.execute("SELECT * FROM occupation WHERE occ_id = %s", (occ_id,))
            user_data['occupation'] = cursor.fetchone()
        else:
            user_data['occupation'] = {}

        # Fetch Financial Record details
        fin_code = user_data['customer'].get('fin_code')
        if fin_code:
            cursor.execute("SELECT * FROM financial_record WHERE fin_code = %s", (fin_code,))
            user_data['financial_record'] = cursor.fetchone()
        else:
            user_data['financial_record'] = {}
        
        # Fetch Spouse details (if civil status is Married)
        if user_data['customer'].get('civilstatus') == 'Married':
            cursor.execute("SELECT * FROM spouse WHERE cust_no = %s", (cust_no,))
            user_data['spouse'] = cursor.fetchone()
        else:
            user_data['spouse'] = None # Explicitly set to None if not married

        # Fetch Employer Details (via employment_details if exists)
        user_data['employer_details'] = None # Default to None
        cursor.execute("SELECT emp_id FROM employment_details WHERE cust_no = %s", (cust_no,))
        emp_link = cursor.fetchone()
        if emp_link and emp_link['emp_id']:
            cursor.execute("SELECT * FROM employer_details WHERE emp_id = %s", (emp_link['emp_id'],))
            user_data['employer_details'] = cursor.fetchone()

        # Fetch Company Affiliations
        cursor.execute("SELECT * FROM company_affiliation WHERE cust_no = %s", (cust_no,))
        user_data['company_affiliations'] = cursor.fetchall()
        
        # Fetch Existing Bank Accounts (and their associated bank details)
        sql_existing_banks = """
            SELECT eb.acc_type, bd.bank_name, bd.branch 
            FROM existing_bank eb
            JOIN bank_details bd ON eb.bank_code = bd.bank_code
            WHERE eb.cust_no = %s
        """
        cursor.execute(sql_existing_banks, (cust_no,))
        user_data['existing_banks'] = cursor.fetchall()

        # Fetch Public Official Relationships
        sql_po_relationships = """
            SELECT cpr.relation_desc, pod.gov_int_name, pod.official_position, pod.branch_orgname
            FROM cust_po_relationship cpr
            JOIN public_official_details pod ON cpr.gov_int_id = pod.gov_int_id
            WHERE cpr.cust_no = %s
        """
        cursor.execute(sql_po_relationships, (cust_no,))
        user_data['public_official_relationships'] = cursor.fetchall()


        return render_template('userHome.html', user_data=user_data)

    except mysql.connector.Error as err:
        print(f"DB error fetching user home data: {err}")
        return "Database error while loading your profile.", 500
    except Exception as e:
        print(f"Unexpected error fetching user home data: {e}")
        return "An unexpected error occurred while loading your profile.", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/admin_dashboard')
def admin_dashboard():
    # Only allow access if admin is logged in
    if 'admin' not in session:
        return redirect('/login')

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Database connection failed")

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.cust_no, c.custname, c.email_address, c.contact_no
            FROM customer c
            ORDER BY c.cust_no DESC
        """)
        customers = cursor.fetchall()

        return render_template('admin_dashboard.html', customers=customers)

    except mysql.connector.Error as err:
        print(f"DB error in admin_dashboard: {err}")
        return "Database error while loading admin dashboard", 500
    except Exception as e:
        print(f"Unexpected error in admin_dashboard: {e}")
        return "Unexpected error while loading dashboard", 500
    finally:
        if cursor: # Check if cursor exists before closing
            cursor.close()
        if conn:
            conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/login')


@app.route('/admin/delete_customer', methods=['POST'])
def delete_customer():
    """
    Deletes a customer and all their associated records across all related tables
    in a transactional manner.
    """
    if 'admin' not in session:
        return redirect('/login')

    cust_no = request.form.get('cust_no')
    
    if not cust_no:
        return "Customer ID is missing", 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            return "Database connection failed", 500
        
        cursor = conn.cursor()
        conn.start_transaction() # Start a transaction for atomicity

        # --- 1. Retrieve IDs of related records before deletion ---
        occ_id = None
        fin_code = None
        emp_id = None
        gov_int_ids = [] # A customer can be related to multiple public officials
        
        # Get occ_id and fin_code from the customer table
        cursor.execute("SELECT occ_id, fin_code FROM customer WHERE cust_no = %s", (cust_no,))
        customer_info = cursor.fetchone()
        if customer_info:
            occ_id, fin_code = customer_info
        
        # Get emp_id from employment_details (if exists)
        cursor.execute("SELECT emp_id FROM employment_details WHERE cust_no = %s", (cust_no,))
        emp_info = cursor.fetchone()
        if emp_info:
            emp_id = emp_info[0]

        # Get gov_int_ids from cust_po_relationship (can be multiple)
        cursor.execute("SELECT gov_int_id FROM cust_po_relationship WHERE cust_no = %s", (cust_no,))
        gov_int_results = cursor.fetchall()
        gov_int_ids = [row[0] for row in gov_int_results]

        # --- 2. Delete from child tables directly referencing cust_no ---
        # The order here is important if you don't have ON DELETE CASCADE set up for all FKs.
        # It's safer to delete records in tables that depend on `cust_no` first.
        cursor.execute("DELETE FROM credentials WHERE cust_no = %s", (cust_no,)) 
        cursor.execute("DELETE FROM employment_details WHERE cust_no = %s", (cust_no,))
        cursor.execute("DELETE FROM spouse WHERE cust_no = %s", (cust_no,))
        cursor.execute("DELETE FROM company_affiliation WHERE cust_no = %s", (cust_no,))
        cursor.execute("DELETE FROM existing_bank WHERE cust_no = %s", (cust_no,))
        cursor.execute("DELETE FROM cust_po_relationship WHERE cust_no = %s", (cust_no,))

        # --- 3. Delete from indirectly linked tables (employer_details, public_official_details) ---
        # These deletions depend on IDs retrieved from intermediate tables (employment_details, cust_po_relationship).
        if emp_id:
            cursor.execute("DELETE FROM employer_details WHERE emp_id = %s", (emp_id,))
        
        if gov_int_ids:
            for gov_id in gov_int_ids:
                cursor.execute("DELETE FROM public_official_details WHERE gov_int_id = %s", (gov_id,))
        
        # --- 4. Delete the main customer record ---
        cursor.execute("DELETE FROM customer WHERE cust_no = %s", (cust_no,))

        # --- 5. Delete from parent tables whose records are now orphaned (occupation, financial_record) ---
        # These are deleted last because the customer record referenced them.
        if occ_id:
            cursor.execute("DELETE FROM occupation WHERE occ_id = %s", (occ_id,))
        if fin_code:
            cursor.execute("DELETE FROM financial_record WHERE fin_code = %s", (fin_code,))

        conn.commit() # Commit the transaction if all deletions are successful

        return redirect('/admin_dashboard')

    except mysql.connector.Error as err:
        if conn:
            conn.rollback() # Rollback on database error
        print(f"DB delete error: {err}")
        return "Failed to delete customer and related data. Error: " + str(err), 500
    except Exception as e:
        if conn:
            conn.rollback() # Rollback on unexpected error
        print(f"Unexpected delete error: {e}")
        return "An unexpected error occurred during deletion: " + str(e), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --- Main execution block ---
if __name__ == '__main__':
    # Run schema updates/migrations on app startup.
    # In a production environment, this should be handled by dedicated migration tools.
    _ensure_database_schema()

    # Use 0.0.0.0 to make the Flask app accessible from any IP address
    # This is important for environments where Flask is run inside a container (e.g., Docker)
    app.run(host='0.0.0.0', port=0000, debug=True) # Corrected port to 5000
