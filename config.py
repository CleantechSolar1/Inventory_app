import os
import urllib.parse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
 
    # Configure connection to MS Access database via ODBC
    DRIVER = '{Microsoft Access Driver (*.mdb, *.accdb)}'
    DBQ = r'C:\Users\SameerMishra\Inventory_app\Asset.accdb'
 
    # Create the connection string and encode it properly
    conn_str = f'DRIVER={DRIVER};DBQ={DBQ};'
    conn_str_encoded = urllib.parse.quote_plus(conn_str)
 
    # Set the SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_DATABASE_URI = f'access+pyodbc:///?odbc_connect={conn_str_encoded}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
