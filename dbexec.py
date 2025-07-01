import os

# Specify the path to the database file
db_file = "articles.db"

# Check if the file exists and delete it
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"{db_file} has been deleted.")
else:
    print(f"{db_file} does not exist.")
