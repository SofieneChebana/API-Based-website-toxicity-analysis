import os
import sys
import pickle
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from scraping import loadPages
from analysis import getScores
import DBHandler
import API
current_dir = os.path.dirname(os.path.abspath(__file__))
eval_dir = os.path.join(current_dir, "evaluation/")
reseau_dir = os.path.join(eval_dir,"reseau/")
parseContent_dir = os.path.join(eval_dir,"webcontents/")
sys.path.insert(1, eval_dir)
sys.path.insert(2,reseau_dir)
sys.path.insert(3,parseContent_dir)
import ParseContent
import Reseau
import Evaluation

class Model:

    def __init__(self, data):
        
        X = [[element[0]] for element in data]
        X = np.array(X)
        y = [element[1] for element in data] #Labellisation des données.
        X.reshape(-1, 1)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.3)


    def getClassifier(self):
        return self.clf


    def train(self):

        clf = svm.SVC()
        clf.fit(self.X_train, self.y_train)

        self.clf = clf

    
    def getAccuracy(self):
        y_predict = self.clf.predict(self.X_test)

        return accuracy_score(self.y_test, y_predict)


if __name__ == "__main__":
    #Récupération des urls.
    dbh = DBHandler.DBHandler('../dataset/bdd/projet.db')
    dbh.connecter()
    urls = dbh.requete("SELECT URL FROM ALL_URL")[1]
    dbh.deconnecter()

    
    #Calculs des scores de chaque url.
    rx = Reseau.Reseau()
    pc = ParseContent.ParseContent()
    api = API.APIAnalyzer()

    eval = Evaluation.Evaluation(pc,api,rx)
    #eval.reset_ALL_URL()
    
    data = eval.evaluate_all_url()
    
    
    
        
    model = Model(data)
    print("Training...")
    model.train()
    print("The accuracy is ", model.getAccuracy())
    clf = model.getClassifier()


    file = "classifier.pkl"
    with open(file, 'wb') as file:
        pickle.dump(clf, file)

    print("The classifier has been saved in the 'classifier.pkl' file.")
