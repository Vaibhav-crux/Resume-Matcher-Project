import sqlite3

def drop_table(db_path, table_name):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # SQL query to drop the table if it exists
        drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(drop_table_query)

        # Commit the changes and close the connection
        conn.commit()
        print(f"Table '{table_name}' has been deleted (if it existed).")

    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()

# Path to your SQLite database
db_path = r"D:\Project\Company Assignment\eduBild\resume_analyzer\db.sqlite3"

# Table name to drop
table_name = "candidates_resume_candidateprofile"

# Call the function to drop the table
drop_table(db_path, table_name)
