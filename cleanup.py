import sqlite3
from datetime import datetime

def clean_database():
    # Connect to existing database
    conn = sqlite3.connect('cves.db')
    cursor = conn.cursor()

    
    cursor.execute('''
        DELETE FROM cve 
        WHERE 
            id IS NULL OR 
            published IS NULL OR 
            last_modified IS NULL OR
            base_score_v2 IS NULL
    ''')
    print(f"Removed {cursor.rowcount} rows with null values")

    
    cursor.execute('''
        DELETE FROM cve 
        WHERE rowid NOT IN (
            SELECT MIN(rowid) 
            FROM cve 
            GROUP BY id
        )
    ''')
    print(f"Removed {cursor.rowcount} duplicate rows")


    conn.commit()
    conn.close()

if __name__ == "__main__":
    clean_database()
    print("Database cleanup completed!")
