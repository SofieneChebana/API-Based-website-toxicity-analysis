import sqlite3

"""
Class built to interact with a Sqlite database.
@path : The path towards the database
"""
class DBHandler:
    
    def __init__(self, path):
        self.path = path
        self.cursor = None
        self.connection = None

    def getCursor(self):
            return self.cursor
        
    def getConnection(self):
        return self.connection


    
    """
    Database connection function.
    @return : The cursor of the database in order to make requests.
    """
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.path)
            self.cursor = self.connection.cursor()
        except:
            print("Connection to " + self.path + " failed.")
            print(self, ": cursor and connection failed to establish.")
        return self.cursor

    
    
    """
    Database disconnection function.
    """
    def disconnect(self):
        self.connection.close()


    
    """
    Function that takes a SQL query and return its result.
    @request : (string) the SQL query to execute.
    @return : (string, list) result of the SQL query.
    """
    def query(self, request : str, parameters = ()):
        req = None

        try:
            req = self.cursor.execute(request, parameters) # query all_url
            self.connection.commit()
        except:
            print("La requête a échoué")
        return req.fetchall()