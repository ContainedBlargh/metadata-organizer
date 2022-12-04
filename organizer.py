# Import the necessary modules
import os
import sqlite3
import mimetypes
import re
import PyPDF2
import pyaudio
import nltk
from rake_nltk import Rake
import sys

# Define a function to extract metadata from a file
def extract_file_metadata(path, name):
    print(path, name)
    # Get the name and location of the file
    location = path
    text = ""
    duration = 0
    keywords = []
    type = ""
    # Use the mimetypes library to guess the MIME type of the file
    tname = os.path.basename(path)
    mtype = mimetypes.guess_type(tname)[0]
    if mtype:
        type = mtype
    if name.endswith(".md") or name.endswith(".MD"):
        type = "text/markdown"

    print(f"name: {name}, type: {type}")
    # Get the size of the file
    size = os.path.getsize(path)
    headings = []

    # If the file is a pdf file, extract the text and keywords
    if type == 'application/pdf':
        # Open the file and extract the text and keywords
        with open(path, 'rb') as f:
            try:
                # Use PyPDF2 to extract the text from the pdf file
                text = PyPDF2.PdfFileReader(f).getPage(0).extractText()
                r = Rake()
                r.extract_keywords_from_text(text)
                keywords = r.get_ranked_phrases()
            except Exception as e:
                text = ""


    # If the file is a markdown file, extract the headings and keywords
    if type == 'text/markdown':
        # Open the file and extract the headings and keywords
        with open(path, 'r') as f:
            # Use a regular expression to find all lines starting with one or more #-characters
            try:
                text = "\n".join(f.readlines())
                headings = re.findall(r'^#+ .*', text, re.MULTILINE)

                # Use the spaCy model to extract keywords from the markdown file
                r = Rake()
                r.extract_keywords_from_text(text)
                keywords = r.get_ranked_phrases()
            except:
                pass

    # If the file is a media file, extract the duration and keywords
    # if type in ['audio/mpeg', 'video/mp4']:
    #     # Open the file and extract the duration and keywords
    #     with open(path, 'rb') as f:
    #         # Use PyAudio to extract the duration of the media file
    #         duration = pyaudio.get_duration(f)

    # Return a dictionary with the metadata
    return {
        'name': name,
        'location': location,
        'type': type,
        'size': size,
        'num_files': 0,
        'num_subfolders': 0,
        'text': text,
        'duration': duration,
        'headings': ','.join(headings),
        'keywords': ','.join(keywords)
    }


def extract_folder_metadata(path, name):
    # Get the name and location of the folder
    
    location = path
    type = 'folder'

    # Get the number of files and subfolders in the folder
    num_files = len(os.listdir(path))
    num_subfolders = len([x for x in os.listdir(path) if os.path.isdir(x)])

    # Return a dictionary with the metadata
    return {
        'name': name,
        'location': location,
        'type': type,
        'size': 0,
        'num_files': num_files,
        'num_subfolders': num_subfolders
    }

# Define a function to insert metadata into the database
def insert_metadata(metadata):
    # Connect to the metadata database
    conn = sqlite3.connect('metadata.db')
    cursor = conn.cursor()

    # Insert the metadata into the database
    cursor.execute('''
        INSERT INTO metadata (
            name,
            location,
            type,
            size,
            num_files,
            num_subfolders,
            text,
            duration,
            headings,
            keywords
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metadata['name'],
        metadata['location'],
        metadata['type'],
        metadata['size'],
        metadata['num_files'],
        metadata['num_subfolders'],
        metadata.get('text', None),
        metadata.get('duration', None),
        metadata.get('headings', None),
        metadata.get('keywords', None)
    ))

    # Commit the changes to the database
    conn.commit()

    # Close the database connection
    conn.close()

# Define the main function
def main(path):
    nltk.download('stopwords')

    # Create a database connection and a cursor object
    conn = sqlite3.connect('metadata.db')
    cursor = conn.cursor()

    # Create the table to store the metadata
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metadata'")
    if cursor.fetchone():
        cursor.execute('DROP TABLE metadata')
    cursor.execute('''
        CREATE TABLE metadata (
            name text,
            location text,
            type text,
            size integer,
            num_files integer,
            num_subfolders integer,
            text text,
            duration integer,
            headings text,
            keywords text
        )
    ''')

    # Iterate over all the files and folders in the current directory
    for root, dirs, files in os.walk(path):
        # Extract metadata from each file
        for file in files:
            file_path = os.path.join(root, file)
            if ".git" in file_path:
                continue
            metadata = extract_file_metadata(file_path, file)
            insert_metadata(metadata)

        # Extract metadata from each folder
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            metadata = extract_folder_metadata(dir_path, dir)
            insert_metadata(metadata)

# Call the main function
if __name__ == '__main__':
    main(sys.argv[1])
