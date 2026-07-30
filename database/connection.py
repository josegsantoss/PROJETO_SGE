import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123", 
            database="tcc_3tdsa"           
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None
