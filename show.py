# Import the necessary modules
import sqlite3
from flask import Flask, render_template

# Create a Flask app
app = Flask(__name__, template_folder='templates')

DATABASE_FILE = 'metadata.db'

def query_metadata(template_name=None):
    # Open a connection to the database
    conn = sqlite3.connect(DATABASE_FILE)

    try:
        # Create a cursor to execute SQL commands
        cursor = conn.cursor()

        # Check if a template name was specified
        if template_name is not None:
            # Query the database for the metadata row with the specified template name
            cursor.execute('SELECT * FROM metadata WHERE name = ?', (template_name,))
        else:
            # Query the database for all metadata rows
            cursor.execute('SELECT * FROM metadata')

        # Fetch the query results
        results = cursor.fetchall()

        # Get the column names for the metadata table
        column_names = [column[0] for column in cursor.description]

        # Return the query results as a list of dictionaries
        return [dict(zip(column_names, row)) for row in results]
    finally:
        # Close the connection to the database
        conn.close()



@app.route('/template/<template_name>')
def show_template(template_name):
    # Query the database for the metadata row with the specified template name
    metadata = query_metadata(template_name)
    # Render the metadata.html template and pass the metadata as a parameter
    return render_template('metadata.html', metadata=metadata)

@app.route('/')
def index():
    # Query the database for all metadata rows
    metadata = query_metadata()

    # Render the index.html template and pass the metadata as a parameter
    return render_template('index.html', metadata=metadata)

# Run the Flask app
if __name__ == '__main__':
    app.run()
