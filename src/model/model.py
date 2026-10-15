import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score


class Model:

    def __init__(self, data):

        X = [[element[0], element[1], element[2], element[3], element[4], element[6]] for element in data]
        X = np.array(X)
        y = [element[5] for element in data] #Labellisation of the data.
        #X.reshape(-1, 1)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.3)


        
    def getClassifier(self):
        return self.clf


    
    def train(self):

        self.clf = svm.SVC()
        self.clf.fit(self.X_train, self.y_train)



    def getInfo(self):

        y_predict = self.clf.predict(self.X_test)

        print("Number of samples        : ", len(self.X_train))
        print("Number of toxic url      : ", sum(self.y_train))
        print("Number of non toxic url  :",  len(self.y_train) - sum(self.y_train))
        print("Accuracy                 : ", accuracy_score(self.y_test, y_predict))
        print("F1-Score                 :", f1_score(self.y_test, y_predict))



