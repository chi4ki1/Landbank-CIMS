-- Create database
CREATE DATABASE IF NOT EXISTS database_landbank;
USE database_landbank;

-- Occupation table with auto-increment ID but keeping occ_id as display ID
CREATE TABLE IF NOT EXISTS occupation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    occ_id VARCHAR(10) UNIQUE NOT NULL,
    occ_type VARCHAR(255),
    bus_nature VARCHAR(255)
);

-- Financial record table
CREATE TABLE IF NOT EXISTS financial_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fin_code VARCHAR(10) UNIQUE NOT NULL,
    source_wealth VARCHAR(255),
    mon_income VARCHAR(255),
    ann_income VARCHAR(255)
);

-- Employer details table
CREATE TABLE IF NOT EXISTS employer_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(10) UNIQUE NOT NULL,
    tin_id VARCHAR(50),
    empname VARCHAR(255),
    emp_address VARCHAR(255),
    phonefax_no VARCHAR(50),
    job_title VARCHAR(255),
    emp_date DATE
);

-- Customer table (main table)
CREATE TABLE IF NOT EXISTS customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cust_no VARCHAR(10) UNIQUE NOT NULL,
    custname VARCHAR(255),
    datebirth DATE,
    nationality VARCHAR(255),
    citizenship VARCHAR(255),
    custsex VARCHAR(10),
    placebirth VARCHAR(255),
    civilstatus VARCHAR(50),
    num_children INT,
    mmaiden_name VARCHAR(255),
    cust_address VARCHAR(255),
    email_address VARCHAR(255),
    contact_no VARCHAR(20),
    occ_id VARCHAR(10),
    fin_code VARCHAR(10),
    status VARCHAR(20) DEFAULT 'Active',
    FOREIGN KEY (occ_id) REFERENCES occupation(occ_id),
    FOREIGN KEY (fin_code) REFERENCES financial_record(fin_code)
);

-- Employment details (linking table) - Modified to remove empd and id
CREATE TABLE IF NOT EXISTS employment_details (
    cust_no VARCHAR(10),
    emp_id VARCHAR(10),
    PRIMARY KEY (cust_no, emp_id),
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no),
    FOREIGN KEY (emp_id) REFERENCES employer_details(emp_id)
);

-- Spouse table
CREATE TABLE IF NOT EXISTS spouse (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sp_code VARCHAR(10),
    cust_no VARCHAR(10),
    sp_name VARCHAR(255),
    sp_datebirth DATE,
    sp_profession VARCHAR(255),
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no)
);

-- Company affiliation table
CREATE TABLE IF NOT EXISTS company_affiliation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cust_no VARCHAR(10),
    depositor_role VARCHAR(255),
    dep_compname VARCHAR(255),
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no)
);

-- Bank details table
CREATE TABLE IF NOT EXISTS bank_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bank_code VARCHAR(10) UNIQUE NOT NULL,
    bank_name VARCHAR(255),
    branch VARCHAR(255)
);

-- Existing bank accounts table
CREATE TABLE IF NOT EXISTS existing_bank (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cust_no VARCHAR(10),
    bank_code VARCHAR(10),
    acc_type VARCHAR(255),
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no),
    FOREIGN KEY (bank_code) REFERENCES bank_details(bank_code)
);

-- Public official details table
CREATE TABLE IF NOT EXISTS public_official_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gov_int_id VARCHAR(10) UNIQUE NOT NULL,
    gov_int_name VARCHAR(255),
    official_position VARCHAR(255),
    branch_orgname VARCHAR(255)
);

-- Customer-public official relationship table
CREATE TABLE IF NOT EXISTS cust_po_relationship (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cust_no VARCHAR(10),
    gov_int_id VARCHAR(10),
    relation_desc VARCHAR(255),
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no),
    FOREIGN KEY (gov_int_id) REFERENCES public_official_details(gov_int_id)
);

-- Credentials table
CREATE TABLE IF NOT EXISTS credentials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cust_no VARCHAR(10),
    username VARCHAR(255),
    password VARCHAR(255),
    FOREIGN KEY (cust_no) REFERENCES customer(cust_no)
);



USE database_landbank;



-- Insert into occupation table
INSERT INTO occupation (occ_id, occ_type, bus_nature)
VALUES
('OC01', 'Employed', 'C1033 - Manufacturing'),
('OC02', 'Employed', 'Q8688 - Human Health and Social Work Activities'),
('OC03', 'Housewife', 'V0002 - Others - Unemployed/Housewife'),
('OC04', 'Lawyers/Notary/Independent Legal Professional/Accountant', 'M6975 - Professional, Scientific, and Technical Activities'),
('OC05', 'Student/Minor', 'V0001 - Others - Student/Minor/Retiree/Pensioner'),
('OC06', 'Employed', 'Q8688 - Human Health and Social Work Activities'),
('OC07', 'Self-Employed', 'G4547 - Wholesale and Retail Trade, Repair of Motor Vehicles and Motorcycles'),
('OC08', 'Government Official', 'O6400 - Public Administrative and Defense, Compulsory Social Security'),
('OC09', 'Housewife', 'V0002 - Others - Unemployed/Housewife'),
('OC10', 'Unemployed', '9200 - Gambling and Betting Activities'),
('OC11', 'Employed', 'N7782 - Administrative and Support Service Activities'),
('OC12', 'OFW/Overseas Filipino', 'Q8688 - Human Health and Social Work Activities'),
('OC13', 'Lawyers/Notary/Independent Legal Professional/Accountant', 'O6400 - Public Administrative and Defense, Compulsory Social Security');

-- Insert into financial_record table
INSERT INTO financial_record (fin_code, source_wealth, mon_income, ann_income)
VALUES
('F1', 'Salary/Honoraria, Professional Fees - Others, Interest/Commission', 'Php 50,000.01-100,000.00', 'Php 600,000.01-1,200,000.00'),
('F2', 'Salary/Honoraria, Other Remittance, Business', 'Php 30,000.01-50,000.00', 'Php 360,000.01-600,000.00'),
('F3', 'Allowance, Sale of Assets, Donations/Inheritance', 'Php 30,000.00 and below', 'Php 360,000.00 and below'),
('F4', 'Salary/Honoraria, Professional Fees - Lawyers/Notary/Independent, Fees and Charges', 'Php 30,000.01-50,000.00', 'Php 360,000.01-600,000.00'),
('F5', 'Donations/Inheritance, Allowance, Grant/Scholarship/Awards/Prizes/Benefits', 'Php 30,000.01-50,000.00', 'Php 360,000.01-600,000.00'),
('F6', 'Salary/Honoraria, Professional Fees - Others, Fees and Charges', 'Php 50,000.01-100,000.00', 'Php 600,000.01-1,200,000.00'),
('F7', 'Business, Pension, Sale of Assets', 'Php 30,000.00 and below', 'Php 360,000.00 and below'),
('F8', 'Salary/Honoraria, Professional Fees - Others, Government Appropriation', 'Php 50,000.01-100,000.00', 'Php 600,000.01-1,200,000.00'),
('F9', 'Regular remittance, Sale of Assets, Loans', 'Php 30,000.01-50,000.00', 'Php 360,000.01-600,000.00'),
('F10', 'Regular Remittance, Loans, Others - Without documents', 'Php 30,000.00 and below', 'Php 360,000.00 and below'),
('F11', 'Salary/Honoraria, Interest/Commission, Loans', 'Php 30,000.01-50,000.00', 'Php 360,000.01-600,000.00'),
('F12', 'Salary/Honoraria, Other Remittance, Others - without documents', 'Php 50,000.01-100,000.00', 'Php 600,000.01-1,200,000.00'),
('F13', 'Salary/Honoraria, Grant/Scholarship/Awards/Prices/Benefits, Others - with documents', 'Php 30,000.01-50,000.00', 'Php 360,000.01-600,000.00'),
('F14', 'Salary/Honoraria, Donations/Inheritance, Professional Fees - Others', 'Php 50,000.01-100,000.00', 'Php 600,000.01-1,200,000.00'),
('F15', 'Professional Fees - Lawyers/Notary/Independent, Sales of Assets, Taxes and Licenses', 'Php 100,000.01-500,000.00', 'Php 1,200,000.01-6,000,000.00');

-- Insert into employer_details table
INSERT INTO employer_details (emp_id, tin_id, empname, emp_address, phonefax_no, job_title, emp_date)
VALUES
('EMP01', '123-456-789-000', 'DEF Corporation', '123 Mahogany St, Quezon City, 1008', '(02) 1232-4567', 'Project Manager', '2021-01-15'),
('EMP02', '243-816-172-000', 'PwC Philippines', '29th Philamlife Tower, Makati City, 1227', '(02) 8843-8754', 'Dentist', '2014-02-17'),
('EMP03', '213-543-219-000', 'NoJustice Firm', '109 Mahabang Daan, Valenzuela City, 1440', '(02) 1433-3245', 'Chief Legal Officer', '2022-12-28'),
('EMP04', '456-980-367-000', 'Pasay City General Hospital', '18 Burgos Street, Pasay City, 1304', '(02) 8831-8981', 'Doctor', '2005-09-01'),
('EMP05', '765-309-564-000', 'Department of the Interior and Local Government', '10 Francisco Street, Brgy Del Monte, Quezon City, 1008', '(02) 8925-0349', 'Regional Director', '2013-07-15'),
('EMP06', '276-345-921-000', 'Global Telecom Services', '2nd Floor, 11th Tower Boli, Manila City, 1014', '(02) 8656-4533', 'Customer Service Representative', '2019-11-23'),
('EMP07', '324-875-789-000', 'Masking Call', '20 Aruga, Brgy Kulang, Iloilo City, 5000', '(033) 321-9834', 'Customer Service Representative', '2021-10-09'),
('EMP08', '876-593-078-000', 'Telecomms Company', '21 Turon, Brgy Kalampag, Isabela City, 3300', '+63 62 300-3346', 'Customer Service Representative', '2024-03-27'),
('EMP09', '424-290-411-000', 'Geneva University Hospital', 'Rue Willy-Donze 6, 1205 Geneva, Switzerland', '+41 22 372 47 42', 'Nurse', '2020-08-19'),
('EMP10', '983-019-313-000', 'NoJustice Firm', '109 Mahabang Daan, Valenzuela City, 1440', '(02) 8342-4398', 'Lawyer', '2024-06-25');

-- Insert into customer table
INSERT INTO customer (cust_no, custname, datebirth, nationality, citizenship, custsex, placebirth, civilstatus, mmaiden_name, num_children, cust_address, email_address, contact_no, occ_id, fin_code)
VALUES
('C001', 'Mavis Cruz Garcia', '1998-09-25', 'Filipino', 'Filipino', 'Female', 'Antipolo City', 'Married', 'Nora Rivera Cruz', 2, '50 Marcos Highway, Antipolo City, 1870', 'mavis.garcia25@gmail.com', '0928-934-5708', 'OC01', 'F1'),
('C002', 'Archie Toribio Anderson', '1979-02-08', 'Canadian', 'Filipino', 'Male', 'Toronto, Canada', 'Married', 'Marie Castro Martinez', 3, '39th avenue Fairlane Brgy. Nangka, Marikina City, 1811', 'archietanderson@gmail.com', '0916-543-9877', 'OC02', 'F2'),
('C003', 'Ariana Cruz Dominguez', '1991-07-14', 'Filipino', 'Filipino', 'Female', 'Manila City', 'Married', 'Charo Santos Cruz', 1, '1733 G. Tuazon Street, Sampaloc, Manila City, 1008', 'arianadominguez14@gmail.com', '0908-625-2213', 'OC03', 'F3'),
('C004', 'Roberto Dimasalang Rosales', '1989-10-20', 'Filipino', 'Filipino', 'Male', 'Valenzuela City', 'Single', 'Katy Perez Dimasalang', 0, '20 Mabuhay St, Valenzuela City, 1440', 'robertorosales2000@gmail.com', '0941-890-0999', 'OC04', 'F4'),
('C005', 'Shawn Castro Domingo', '2005-02-15', 'Filipino', 'Filipino', 'Male', 'Tagbilaran City', 'Single', 'Shiella Rose Ramos Castro', 0, '3233 Maple Street, Brgy San Juan, San Juan City, 1500', 'shawn.c.domingo@gmail.com', '0939-678-2543', 'OC05', 'F5'),
('C006', 'Nora Aguirre Marasigan', '1979-09-30', 'Filipino', 'Filipino', 'Female', 'Dasmarinas City', 'Widowed', 'Alina De Mesa Aguirre', 4, '661 Protacio Ext, Barangay 153, Pasay City, 1304', 'nora.aguirre@gmail.com', '0915-436-0987', 'OC06', 'F6'),
('C007', 'Juan Samson Tenorio', '1960-06-23', 'Filipino', 'Filipino', 'Male', 'Tagaytay City', 'Widowed', 'Rhodette Marcelino Samson', 8, '649 R. Hidalgo Street, Brgy 307 Quiapo, City of Manila, Metro Manila 1001', 'tenorio.juan23@gmail.com', '0981-657-1236', 'OC07', 'F7'),
('C008', 'John Danilo Pimentel', '1974-04-13', 'Filipino', 'Filipino', 'Male', 'Taguig City', 'Married', 'Jaimelyn Galang Pimentel', 4, '789 Pine Road, Brgy West, Quezon City, 1100', 'john.pimentel1@gmail.com', '0967-776-0279', 'OC08', 'F8'),
('C009', 'Mary Ann Jones Buenaventura', '1985-03-02', 'American', 'Filipino', 'Female', 'Oklahoma, America', 'Married', 'Amelia Brown Jones', 6, '4041 Ash Lane, Brgy San Roque, Makati City, 1200', 'mary.jones@outlook.com', '0923-234-4567', 'OC09', 'F9'),
('C010', 'Mark Arvin Prado Rosales', '1997-12-10', 'Filipino', 'Filipino', 'Male', 'Manila City', 'Married', 'Leslie Agustin Prado', 1, '130 Boni Street, Brgy Kunis, Manila City, 1014', 'arvinprado2@gmail.com', '0967-156-3789', 'OC10', 'F10'),
('C011', 'Gracelyn Basa Rosales', '1999-05-14', 'Filipino', 'Filipino', 'Female', 'Manila City', 'Married', 'Angelou Trinidad Basa', 1, '130 Boni Street, Brgy Kunis, Manila City, 1014', 'rosales.gracelyn1999@gmail.com', '0987-092-4563', 'OC11', 'F11'),
('C012', 'Phaedra Viernes Cordero', '2001-10-16', 'Filipino', 'Filipino', 'Female', 'Iloilo City', 'Single', 'Acadia Espino Viernes', 1, '76 Matubis, Brgy San Pedro, Iloilo CIty, 5000', 'phaedra16cordero@gmail.com', '0924-564-9812', 'OC11', 'F12'),
('C013', 'Krisha Gallardo Duran', '2003-11-18', 'Filipino', 'Filipino', 'Female', 'Isabela City', 'Single', 'Jezel Manansala Gallardo', 0, '67 Pochi Street, Brgy Cosi, Isabela City, 3300', 'duran.krisha@gmail.com', '0965-999-6755', 'OC11', 'F13'),
('C014', 'Aaliyah Quirante Benitez', '1995-01-25', 'Filipino', 'Filipino', 'Female', 'San Fernando City', 'Single', 'Caia Diam Quirante', 0, 'Rue Gabriellle 4, 1205 Geneva, Switzerland', 'aaliyah.benitez25@gmail.com', '0943-099-3423', 'OC12', 'F14'),
('C015', 'Aaron Quirante Benitez', '1995-01-25', 'Filipino', 'Filipino', 'Male', 'San Fernando City', 'Married', 'Caia Diam Quirante', 2, '90 Siru Village, Brgy, Tinapa, Valenzuela City, 1440', 'aaronqbenitez1995@gmail.com', '0998-730-8987', 'OC13', 'F15');

-- Insert into employment_details table (updated without empd and id)
INSERT INTO employment_details (cust_no, emp_id)
VALUES
('C001', 'EMP01'),
('C002', 'EMP02'),
('C004', 'EMP03'),
('C006', 'EMP04'),
('C008', 'EMP05'),
('C011', 'EMP06'),
('C012', 'EMP07'),
('C013', 'EMP08'),
('C014', 'EMP09'),
('C015', 'EMP10');

-- Insert into spouse table
INSERT INTO spouse (sp_code, cust_no, sp_name, sp_datebirth, sp_profession)
VALUES
('SP1', 'C001', 'Zeref Castro Garcia', '1995-12-01', 'Information Security Analysts'),
('SP2', 'C002', 'Joy Alcala Anderson', '1982-11-02', 'HR Specialist'),
('SP3', 'C003', 'Richard Martin Dominguez', '1995-05-04', 'Railroad Engineer'),
('SP4', 'C006', 'Jeorge Ponciano Marasigan', '1979-06-30', 'Deceased'),
('SP5', 'C007', 'Gina Garcia Tenorio', '1965-12-25', 'Deceased'),
('SP6', 'C008', 'Analisa Borja Pimentel', '1980-07-21', 'Housewife'),
('SP7', 'C009', 'Lester Jake Lorenzo Buenaventura', '1984-09-15', 'Real Estate Broker'),
('SP8', 'C010', 'Gracelyn Basa Rosales', '1999-05-14', 'Customer Service Representative'),
('SP9', 'C011', 'Mark Arvin Prado Rosales', '1997-12-10', 'Unemployed'),
('SP10', 'C015', 'Shaira Perez Benitez', '1995-09-30', 'Accountant');

-- Insert into company_affiliation table
INSERT INTO company_affiliation (cust_no, depositor_role, dep_compname)
VALUES
('C001', 'Signatory', 'DEF Corporation'),
('C001', 'Director/Officer/Stockholder', 'DEF Corporation'),
('C001', 'Director/Officer/Stockholder', 'ABC Company'),
('C002', 'Director/Officer/Stockholder', 'FinTech Corporation'),
('C002', 'Signatory', 'XYZ Holdings'),
('C004', 'Signatory', 'NoJustice Firm'),
('C004', 'Director/Officer/Stockholder', 'Kumawala Firm'),
('C006', 'Signatory', 'Wellness Corporation Solutions'),
('C008', 'Director/Officer/Stockholder', 'Department of the Interior and Local Government'),
('C011', 'Signatory', 'Smart Communications'),
('C012', 'Signatory', 'Globe Telecom'),
('C013', 'Signatory', 'Globe Telecom'),
('C014', 'Signatory', 'Geneva University Hospital'),
('C014', 'Director/Officer/Stockholder', 'NoJustice Firm'),
('C015', 'Director/Officer/Stockholder', 'NoJustice Firm'),
('C015', 'Signatory', 'CityLand Corp');

-- Insert into bank_details table
INSERT INTO bank_details (bank_code, bank_name, branch)
VALUES
('B01', 'Philippine National Bank', 'Antipolo'),
('B02', 'Bank of the Philippine Islands', 'Quezon'),
('B03', 'Security Bank Corporation', 'Makati'),
('B04', 'Bank of the Philippine Islands', 'Pasig'),
('B05', 'Metropolitan Bank and Trust Company', 'Manila'),
('B06', 'Land Bank of the Philippines', 'Valenzuela'),
('B07', 'Banco De Oro', 'Isabela'),
('B08', 'Bank of the Philippine Islands', 'Iloilo'),
('B09', 'CIMB Bank', 'Valenzuela'),
('B10', 'UnionBank of the Philippines', 'Valenzuela'),
('B11', 'EastWest Bank', 'Quezon');

UPDATE bank_details
SET bank_name = 'EastWest Bank'
WHERE bank_code = 'B06';

-- Insert into existing_bank table
INSERT INTO existing_bank (cust_no, bank_code, acc_type)
VALUES
('C001', 'B01', 'Savings Account'),
('C001', 'B01', 'Payroll Account'),
('C001', 'B02', 'Checking Account'),
('C002', 'B03', 'Payroll Account'),
('C002', 'B04', 'Savings Account'),
('C003', 'B05', 'Savings Account'),
('C004', 'B06', 'Payroll Account'),
('C004', 'B03', 'Savings Account'),
('C005', 'B03', 'Savings Account'),
('C006', 'B03', 'Savings Account'),
('C007', 'B05', 'Time Deposit Account'),
('C008', 'B02', 'Payroll Account'),
('C008', 'B11', 'Checking Account'),
('C009', 'B03', 'Savings Account'),
('C010', 'B05', 'Savings Account'),
('C011', 'B05', 'Savings Account'),
('C012', 'B08', 'Savings Account'),
('C013', 'B07', 'Savings Account'),
('C014', 'B09', 'Savings Account'),
('C014', 'B06', 'Foreign Currency Account'),
('C015', 'B06', 'Payroll Account'),
('C015', 'B02', 'Checking Account'),
('C015', 'B10', 'Savings Account');

-- Insert into public_official_details table
INSERT INTO public_official_details (gov_int_id, gov_int_name, official_position, branch_orgname)
VALUES
('OFF001', 'Jose Santiago Cruz', 'Congressman', 'House of Representatives'),
('OFF002', 'Manny Cruz Mondragon', 'Congressman', 'House of Representatives'),
('OFF003', 'Camilla Anderson Lacsamana', 'Immigration Officer', 'Executive Branch'),
('OFF004', 'Marvin Toribio Anderson', 'Councilor', 'City Government'),
('OFF005', 'Monica Dimasalang Rosales', 'Commissioner', 'Civil Service Commission'),
('OFF006', 'Poly Tenorio Domingo', 'Chief Justice', 'Supreme Court'),
('OFF007', 'Clark Duran Domingo', 'Mayor', 'City Government'),
('OFF008', 'Nica Alvero Tenorio', 'Governor', 'Provincial Government'),
('OFF009', 'Celeste Casil Garcia', 'Executive Secretary', 'Executive Branch'),
('OFF010', 'Mark Montes Buenaventura', 'Chief of Staff', 'Executive Branch'),
('OFF011', 'Ross Lorenzo Buenaventura', 'Senator', 'Senate'),
('OFF012', 'Lily Mando Lorenzo', 'Mayor', 'City Government'),
('OFF013', 'Sabrina Lucas Cordero', 'Ombudsman', 'Constitutional Office'),
('OFF014', 'Melanie Quirante Benitez', 'Executive Secretary', 'Executive Branch'),
('OFF015', 'Niko Tin Benitez', 'Immigration Officer', 'Executive Branch'),
('OFF016', 'Lucio Rosas Perez', 'Governor', 'Provincial Government');

-- Insert into cust_po_relationship table
INSERT INTO cust_po_relationship (cust_no, gov_int_id, relation_desc)
VALUES
('C001', 'OFF001', 'Uncle'),
('C001', 'OFF002', 'Cousin'),
('C002', 'OFF003', 'Brother'),
('C002', 'OFF004', 'Brother'),
('C003', 'OFF001', 'Grandfather'),
('C004', 'OFF005', 'Niece'),
('C005', 'OFF006', 'Aunt'),
('C005', 'OFF007', 'Grandfather'),
('C007', 'OFF006', 'Cousin'),
('C007', 'OFF008', 'Daughter'),
('C007', 'OFF009', 'Mother-in-Law'),
('C009', 'OFF010', 'Father-in-Law'),
('C009', 'OFF011', 'Brother-in-Law'),
('C009', 'OFF012', 'Mother-in-Law'),
('C012', 'OFF013', 'Aunt'),
('C013', 'OFF007', 'Uncle'),
('C014', 'OFF014', 'Mother'),
('C014', 'OFF015', 'Cousin'),
('C015', 'OFF014', 'Mother'),
('C015', 'OFF015', 'Cousin'),
('C015', 'OFF016', 'Father-in-Law');

-- Insert into credentials table
INSERT INTO credentials (cust_no, username, password)
VALUES
('C001', 'mavis.garcia25@gmail.com', 'encryptedPasswordHere'),
('C002', 'archietanderson@gmail.com', 'encryptedPasswordHere'),
('C003', 'arianadominguez14@gmail.com', 'encryptedPasswordHere'),
('C004', 'robertorosales2000@gmail.com', 'encryptedPasswordHere'),
('C005', 'shawn.c.domingo@gmail.com', 'encryptedPasswordHere'),
('C006', 'nora.aguirre@gmail.com', 'encryptedPasswordHere'),
('C007', 'tenorio.juan23@gmail.com', 'encryptedPasswordHere'),
('C008', 'john.pimentel1@gmail.com', 'encryptedPasswordHere'),
('C009', 'mary.jones@outlook.com', 'encryptedPasswordHere'),
('C010', 'arvinprado2@gmail.com', 'encryptedPasswordHere'),
('C011', 'rosales.gracelyn1999@gmail.com', 'encryptedPasswordHere'),
('C012', 'phaedra16cordero@gmail.com', 'encryptedPasswordHere'),
('C013', 'duran.krisha@gmail.com', 'encryptedPasswordHere'),
('C014', 'aaliyah.benitez25@gmail.com', 'encryptedPasswordHere'),
('C015', 'aaronqbenitez1995@gmail.com', 'encryptedPasswordHere');

USE database_landbank;
DELIMITER $$

CREATE TRIGGER before_insert_customer
BEFORE INSERT ON customer
FOR EACH ROW
BEGIN
  DECLARE last_code VARCHAR(10);
  DECLARE next_number INT;

  SELECT cust_no
  INTO last_code
  FROM customer
  ORDER BY cust_no DESC
  LIMIT 1;

  IF last_code IS NULL THEN
    SET next_number = 1;
  ELSE
    SET next_number = CAST(SUBSTRING(last_code, 2) AS UNSIGNED) + 1;
  END IF;

  SET NEW.cust_no = CONCAT('C', LPAD(next_number, 3, '0'));
END$$


DELIMITER ;

USE database_landbank;


-- sp_code auto increment
DELIMITER $$

CREATE TRIGGER before_insert_spouse
BEFORE INSERT ON spouse
FOR EACH ROW
BEGIN
  DECLARE last_code VARCHAR(5);
  DECLARE next_number INT;

  SELECT sp_code
  INTO last_code
  FROM spouse
  ORDER BY CAST(SUBSTRING(sp_code, 3) AS UNSIGNED) DESC
  LIMIT 1;

  IF last_code IS NULL THEN
    SET next_number = 1;
  ELSE
    SET next_number = CAST(SUBSTRING(last_code, 3) AS UNSIGNED) + 1;
  END IF;

  SET NEW.sp_code = CONCAT('SP', next_number);
END$$

DELIMITER ;


-- occ_id auto increment
DELIMITER $$

CREATE TRIGGER before_insert_occupation
BEFORE INSERT ON occupation
FOR EACH ROW
BEGIN
  DECLARE last_code VARCHAR(10);
  DECLARE next_number INT;
  DECLARE num_part VARCHAR(10);

  SELECT occ_id
  INTO last_code
  FROM occupation
  ORDER BY CAST(SUBSTRING(occ_id, 3) AS UNSIGNED) DESC
  LIMIT 1;

  IF last_code IS NULL THEN
    SET next_number = 1;
  ELSE
    SET next_number = CAST(SUBSTRING(last_code, 3) AS UNSIGNED) + 1;
  END IF;

  IF next_number < 10 THEN
    SET num_part = LPAD(next_number, 2, '0');
  ELSE
    SET num_part = CAST(next_number AS CHAR);
  END IF;

  SET NEW.occ_id = CONCAT('OC', num_part);
END$$

DELIMITER ;


DELIMITER $$

CREATE TRIGGER before_insert_customer
BEFORE INSERT ON customer
FOR EACH ROW
BEGIN
  DECLARE last_code VARCHAR(10);
  DECLARE next_number INT;

  SELECT cust_no
  INTO last_code
  FROM customer
  ORDER BY cust_no DESC
  LIMIT 1;

  IF last_code IS NULL THEN
    SET next_number = 1;
  ELSE
    SET next_number = CAST(SUBSTRING(last_code, 2) AS UNSIGNED) + 1;
  END IF;

  SET NEW.cust_no = CONCAT('C', LPAD(next_number, 3, '0'));
END$$

DELIMITER ;


-- emp_id auto increment
DELIMITER $$

CREATE TRIGGER before_insert_employer_details
BEFORE INSERT ON employer_details
FOR EACH ROW
BEGIN
  DECLARE last_code VARCHAR(10);
  DECLARE next_number INT;
  DECLARE num_part VARCHAR(10);

  SELECT emp_id
  INTO last_code
  FROM employer_details
  ORDER BY CAST(SUBSTRING(emp_id, 4) AS UNSIGNED) DESC
  LIMIT 1;

  IF last_code IS NULL THEN
    SET next_number = 1;
  ELSE
    SET next_number = CAST(SUBSTRING(last_code, 4) AS UNSIGNED) + 1;
  END IF;

  IF next_number < 10 THEN
    SET num_part = LPAD(next_number, 2, '0');
  ELSE
    SET num_part = CAST(next_number AS CHAR);
  END IF;

  SET NEW.emp_id = CONCAT('EMP', num_part);
END$$

DELIMITER ;

-- fin_code auto increment
DELIMITER $$

CREATE TRIGGER before_insert_financial_record
BEFORE INSERT ON financial_record
FOR EACH ROW
BEGIN
  DECLARE last_code VARCHAR(5);
  DECLARE next_number INT;

  SELECT fin_code
  INTO last_code
  FROM financial_record
  ORDER BY CAST(SUBSTRING(fin_code, 2) AS UNSIGNED) DESC
  LIMIT 1;

  IF last_code IS NULL THEN
    SET next_number = 1;
  ELSE
    SET next_number = CAST(SUBSTRING(last_code, 2) AS UNSIGNED) + 1;
  END IF;

  SET NEW.fin_code = CONCAT('F', next_number);
END$$

DELIMITER ;

-- bank_code auto increment
DELIMITER $$

CREATE TRIGGER before_insert_bank_details
BEFORE INSERT ON bank_details
FOR EACH ROW
BEGIN
  DECLARE last_code VARCHAR(5);
  DECLARE next_number INT;
  DECLARE num_part VARCHAR(3);

  SELECT bank_code
  INTO last_code
  FROM bank_details
  ORDER BY CAST(SUBSTRING(bank_code, 2) AS UNSIGNED) DESC
  LIMIT 1;

  IF last_code IS NULL THEN
    SET next_number = 1;
  ELSE
    SET next_number = CAST(SUBSTRING(last_code, 2) AS UNSIGNED) + 1;
  END IF;

  IF next_number < 10 THEN
    SET num_part = LPAD(next_number, 2, '0');
  ELSE
    SET num_part = CAST(next_number AS CHAR);
  END IF;

  SET NEW.bank_code = CONCAT('B', num_part);
END$$

DELIMITER ;



-- gov_int_id auto increment

DELIMITER $$

CREATE TRIGGER before_insert_public_official_details
BEFORE INSERT ON public_official_details
FOR EACH ROW
BEGIN
  DECLARE last_code VARCHAR(10);
  DECLARE next_number INT;
  DECLARE num_part VARCHAR(3);

  -- Get last gov_int_id ordered by numeric part descending
  SELECT gov_int_id
  INTO last_code
  FROM  public_official_details
  ORDER BY CAST(SUBSTRING(gov_int_id, 4) AS UNSIGNED) DESC
  LIMIT 1;

  IF last_code IS NULL THEN
    SET next_number = 1;
  ELSE
    SET next_number = CAST(SUBSTRING(last_code, 4) AS UNSIGNED) + 1;
  END IF;

  -- Always pad with leading zeros to 3 digits
  SET num_part = LPAD(next_number, 3, '0');

  SET NEW.gov_int_id = CONCAT('OFF', num_part);
END$$

DELIMITER ;


