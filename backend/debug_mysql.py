#!/usr/bin/env python3
"""
MySQL Debug Helper - Check database tables and connection status
Run this script to verify MySQL setup and see what's in the database
"""

import mysql.connector
from mysql.connector import Error
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import config from app.py
try:
    from app import MYSQL_CONFIG
    print("✅ Loaded MYSQL_CONFIG from app.py")
except ImportError:
    print("❌ Could not import from app.py")
    print("Using default config...")
    MYSQL_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'soil_health_db',
        'port': 3306
    }

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_mysql_connection():
    """Check if MySQL server is running and accessible"""
    print_section("🔍 MySQL Connection Check")
    
    print(f"Host: {MYSQL_CONFIG['host']}")
    print(f"Port: {MYSQL_CONFIG['port']}")
    print(f"User: {MYSQL_CONFIG['user']}")
    print(f"Database: {MYSQL_CONFIG['database']}")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print(f"\n✅ MySQL Connection Successful!")
        print(f"   Server version: {conn.get_server_info()}")
        conn.close()
        return True
    except Error as e:
        print(f"\n❌ MySQL Connection Failed!")
        print(f"   Error: {e}")
        print(f"\n💡 Troubleshooting tips:")
        print(f"   1. Is MySQL server running?")
        print(f"      Windows: Check Services or run: net start MySQL80")
        print(f"      Mac: brew services start mysql")
        print(f"      Linux: sudo systemctl start mysql")
        print(f"   2. Is password correct? Update MYSQL_CONFIG['password']")
        print(f"   3. Check credentials:")
        print(f"      mysql -u root -h {MYSQL_CONFIG['host']} -p")
        return False

def list_databases():
    """List all databases"""
    print_section("📋 Available Databases")
    
    try:
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            port=MYSQL_CONFIG['port']
        )
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        print(f"Found {len(databases)} databases:\n")
        for i, (db_name,) in enumerate(databases, 1):
            print(f"  {i}. {db_name}")
        
        cursor.close()
        conn.close()
        
        # Check if our database exists
        db_names = [db[0] for db in databases]
        if MYSQL_CONFIG['database'] in db_names:
            print(f"\n✅ Database '{MYSQL_CONFIG['database']}' exists")
            return True
        else:
            print(f"\n⚠️  Database '{MYSQL_CONFIG['database']}' NOT FOUND")
            print(f"   To create it, run: CREATE DATABASE {MYSQL_CONFIG['database']};")
            return False
    
    except Error as e:
        print(f"❌ Error listing databases: {e}")
        return False

def list_tables():
    """List tables in the soil_health database"""
    print_section("📊 Tables in soil_health_db")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Try to use the database
        try:
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")
        except Error:
            print(f"❌ Database '{MYSQL_CONFIG['database']}' does not exist")
            print(f"   Run: CREATE DATABASE {MYSQL_CONFIG['database']};")
            cursor.close()
            conn.close()
            return False
        
        # Get list of tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"⚠️  No tables found in {MYSQL_CONFIG['database']}")
            print(f"   Run backend once to auto-create tables")
            cursor.close()
            conn.close()
            return False
        
        print(f"Found {len(tables)} tables:\n")
        
        for i, (table_name,) in enumerate(tables, 1):
            print(f"  {i}. {table_name}")
            
            # Show table info
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            print(f"     Rows: {row_count}")
            print(f"     Columns: {len(columns)}")
            
            # Show column details
            for col_name, col_type, null, key, default, extra in columns:
                print(f"       - {col_name} ({col_type})")
            print()
        
        cursor.close()
        conn.close()
        return True
    
    except Error as e:
        print(f"❌ Error listing tables: {e}")
        return False

def show_table_contents():
    """Show contents of sensor_readings table"""
    print_section("📈 Data in sensor_readings Table")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("USE soil_health_db")
        cursor.execute("SELECT COUNT(*) as count FROM sensor_readings")
        count_result = cursor.fetchone()
        total_rows = count_result['count'] if count_result else 0
        
        print(f"Total rows: {total_rows}\n")
        
        if total_rows == 0:
            print("⚠️  No data in sensor_readings table")
            print("   Run sensor generator to populate data")
        else:
            # Show latest 5 readings
            print("Latest 5 readings:\n")
            cursor.execute("""
                SELECT id, timestamp, N, P, K, CO2, temperature, 
                       moisture, pH, health_index, health_status
                FROM sensor_readings
                ORDER BY timestamp DESC
                LIMIT 5
            """)
            
            rows = cursor.fetchall()
            for i, row in enumerate(rows, 1):
                print(f"  {i}. ID: {row['id']}")
                print(f"     Time: {row['timestamp']}")
                print(f"     Health: {row['health_index']}/100 ({row['health_status']})")
                print(f"     N={row['N']:.1f}, P={row['P']:.1f}, K={row['K']:.1f}, CO2={row['CO2']:.1f}")
                print(f"     Temp={row['temperature']:.1f}°C, Moisture={row['moisture']:.1f}%")
                print(f"     pH={row['pH']:.1f}\n")
        
        cursor.close()
        conn.close()
        return True
    
    except Error as e:
        print(f"❌ Error reading table: {e}")
        return False

def show_csv_status():
    """Check CSV file status"""
    print_section("💾 CSV Backup File Status")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'sensor_readings.csv')
    
    if os.path.exists(csv_path):
        size = os.path.getsize(csv_path)
        print(f"✅ CSV file exists")
        print(f"   Path: {csv_path}")
        print(f"   Size: {size:,} bytes")
        
        # Count rows
        try:
            with open(csv_path, 'r') as f:
                lines = f.readlines()
                rows = len(lines) - 1  # Subtract header
                print(f"   Rows: {rows}")
                
                if rows > 0:
                    print(f"\n   Last 3 rows:")
                    for line in lines[-3:]:
                        print(f"   {line.strip()[:80]}...")
        except Exception as e:
            print(f"   Error reading CSV: {e}")
    else:
        print(f"⚠️  CSV file not found")
        print(f"   Path: {csv_path}")
        print(f"   CSV will be created when first data is saved")

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("  MySQL Debug Helper - Checking Database Setup")
    print("="*60)
    
    # Check connection
    connected = check_mysql_connection()
    
    if not connected:
        print("\n" + "="*60)
        print("❌ MySQL Server is NOT Running or Not Accessible")
        print("="*60)
        print("\nTo fix:")
        print("1. Start MySQL server:")
        print("   Windows: net start MySQL80")
        print("2. Verify credentials in app.py")
        print("3. Run this script again")
        return
    
    # Get database info
    has_db = list_databases()
    
    if has_db:
        tables_exist = list_tables()
        if tables_exist:
            show_table_contents()
    
    show_csv_status()
    
    # Final summary
    print_section("✅ Debug Check Complete")
    print("\nNext steps:")
    print("1. If tables exist but are empty:")
    print("   - Start the sensor generator")
    print("   - Or send test data via API")
    print("\n2. If tables don't exist:")
    print("   - Start the backend: python app.py")
    print("   - Tables will auto-create")
    print("\n3. Monitor data flow:")
    print("   - Run this script again to see latest data")
    print("   - Check API: curl http://localhost:5000/api/soil-health/stats")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
