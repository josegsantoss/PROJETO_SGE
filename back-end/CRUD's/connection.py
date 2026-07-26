import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="06022022", # <--- Tem que ser a senha força 100 que criamos!
            database="tcc_sge"           # <--- O nome do banco de dados do seu TCC
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None # É por causa deste None que o erro apareceu!
