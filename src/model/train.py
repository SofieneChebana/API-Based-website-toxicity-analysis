import os
import sys
import pickle
from model import Model

current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(current_dir,"../")
sys.path.insert(1,source_dir)

import DBHandler





if __name__ == "__main__":
    dbh = DBHandler.DBHandler('../../dataset/bdd/projet.db')
    dbh.connect()
    data = dbh.query("SELECT NB_API, NB_ORIGIN_API, COUNTRY, NB_TOXIC_WEBCONTENT, PAGERANK, TOXIC, SCORE FROM ALL_URL_FINAL") #(url, nb_api, origin_api, country, webcontent, pagerank, toxic, score)
    dbh.disconnect()

    """
    print("Computing features for each url...")
    rx = Reseau.Reseau()
    pc = ParseContent.ParseContent()
    api = API.APIAnalyzer()

    eval = Evaluation.Evaluation(pc,api,rx)
    #eval.reset_ALL_URL()
    
    data = eval.evaluate_all_url()
    """
    
    model = Model(data)
    print("Training...")
    model.train()
    model.getInfo()
    clf = model.getClassifier()


    file = "classifier.pkl"
    with open(file, 'wb') as file:
        pickle.dump(clf, file)

    print("The model has been saved in the 'classifier.pkl' file.")