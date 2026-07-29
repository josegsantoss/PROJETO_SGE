# database/connection.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="06022022", # Certifique-se que esta é a senha correta do seu MySQL
        database="tcc_sge"
    )
