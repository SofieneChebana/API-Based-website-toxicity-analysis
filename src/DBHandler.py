import sqlite3

"""
Classe permettant d'intéragir avec une base de données Sqlite
@path : le chemin vers la base de données
"""
class DBHandler:
    
    def __init__(self, path):
        self.path = path
        #nécessaire pour faire des requêtes
        self.curseur = None
        #on établit la connection à la base de données
        self.connection = None

    """
    Fonction permettant de se connecter à une base de données.
    @return : un curseur sur la base de données afin de faire des requêtes
    """
    def connecter(self):
        try:
            self.connection = sqlite3.connect(self.path)
            self.curseur = self.connection.cursor()
        except:
            print("La connection à " + self.path + " a échoué.")
            print(self, ": curseur et connection non établis")
        return self.curseur
    
    """
    Fonction permettant de se déconnecter de la base de données
    """
    def deconnecter(self):
        self.connection.close()
    
    """
    Fonction prenant une commande, et renvoie la commande exécutée et le résultat correspondant
    @commande : (string) une commande à exécuter
    @return : (string, list) la commande exécutée et le résultat correspondant
    """
    def requete(self, commande : str, parameters = ()):
        req = None
        #Utilisation de try et except dans le cas où une commande échoue
        try:
            req = self.curseur.execute(commande, parameters) # query all_url
            self.connection.commit()
        except:
            print("La requête a échoué")
        return commande, req.fetchall()

    def getCurseur(self):
        return self.curseur
    
    def getConnection(self):
        return self.connection