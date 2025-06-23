#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='LandBank@2025',
            database='database_landbank'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def debug_database():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if status column exists
        cursor.execute("DESCRIBE customer")
        columns = cursor.fetchall()
        print("Customer table columns:")
        for col in columns:
            print(f"  {col['Field']}: {col['Type']}")
        
        # Check sample data
        cursor.execute("SELECT cust_no, custname, email_address, status FROM customer LIMIT 5")
        customers = cursor.fetchall()
        print("\nSample customers:")
        for customer in customers:
            print(f"  {customer}")
        
        # Test search query
        print("\nTesting search query...")
        cursor.execute("""
            SELECT c.cust_no, c.custname, c.email_address, c.contact_no, c.status, c.datebirth
            FROM customer c
            WHERE c.custname LIKE %s
        """, ('%Mavis%',))
        results = cursor.fetchall()
        print(f"Search results for 'Mavis': {len(results)} found")
        for result in results:
            print(f"  {result}")
            
    except Error as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    debug_database() 