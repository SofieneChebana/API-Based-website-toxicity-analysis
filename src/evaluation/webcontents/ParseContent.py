#pip install googletrans==4.0.0rc1
#pip install "scipy>=1.7.0,<1.14.0"
#pip install --force-reinstall -v "numpy==1.26.4"
#pip install transformers


import sys

sys.path.append("../../")
import DBHandler
import requests
import time
from locate import get_country

from googletrans import Translator
from bs4 import BeautifulSoup
from transformers import pipeline

power_words = {"achieve",
        "absolutely",
        "action",
        "advantage",
        "adventure",
        "alive",
        "always",
        "available",
        "beautiful",
        "best",
        "brave",
        "brightly",
        "brilliant",
        "change",
        "charming",
        "clean",
        "clever",
        "comfortable",
        "cool",
        "delicious",
        "delight",
        "delightful",
        "difference",
        "discover",
        "easily",
        "energy",
        "enjoy",
        "entirely",
        "essential",
        "everyone",
        "exactly",
        "excellent",
        "excited",
        "exciting",
        "exquisite",
        "extraordinary",
        "focus",
        "free",
        "fresh",
        "friendly",
        "friendship",
        "fully",
        "fun",
        "generous",
        "genius",
        "gift",
        "grand",
        "great",
        "grow",
        "highest",
        "highly",
        "honest",
        "honour",
        "ideal",
        "increase",
        "inspired",
        "instantly",
        "intelligence",
        "knowledge",
        "leader",
        "loving",
        "modern",
        "natural",
        "nice",
        "now",
        "opportunity",
        "passion",
        "perfect",
        "pleasure",
        "popular",
        "positive",
        "powerful",
        "practical",
        "proud",
        "quality",
        "quick",
        "ready",
        "real",
        "really",
        "remarkable",
        "satisfaction",
        "save",
        "simple",
        "special",
        "splendid",
        "strong",
        "superior",
        "truth",
        "understand",
        "unusual",
        "value",
        "vision",
        "wealth",
        "welcome",
        "willing",
        "win",
        "winning",
        "wise",
        "wonderful",
        "worth"}

class ParseContent:

    def __init__(self,fromCrawler=False):
        self.pipeline = pipeline(task="text-classification", model="unitary/toxic-bert", device=0)
        if not fromCrawler:
            self.dbh = DBHandler.DBHandler("../dataset/bdd/projet.db")
            self.dbh.connecter()
            self.dico = self.dicoData()


    def dicoData(self):
        result = {}
        command ,listeOfUrl=self.dbh.requete("Select * from ALL_URL;")
        for link in listeOfUrl:
            result[link[1]] = (link[4],link[5])

        return result
    
    def dicoCountry(self):
        result = {}
        command ,listeOfUrl=self.dbh.requete("Select * from ALL_URL;")
        for link in listeOfUrl:
            result[link[1]] = link[8]
        return result
    
    def getDicoData(self):
        return self.dico
    

    def getCountry(self, url):
        risques = {"KP", "RU", "CN", -1} #pays à risque / pas d'information
        pays = get_country(url)
        return 1 if pays in risques else 0

    #est utilisé dans le crawler
    def nbrPowerWord(self,webContent,translator):
        arrayToCheck = []
        s = BeautifulSoup(webContent,'html.parser')
        #("----------TITRE-------------")

        for titre in s.find_all("title"):
            titreS= titre.string
            if(titreS is not None):
                try:
                    titreS = ' '.join(titreS.split())
                    arrayToCheck.append(translator.translate(titreS,dest='en'))
                except:
                    pass
   
        #("-------------Meta---------------")
        for meta in s.find_all("meta"):
            metaCont = meta.get("content")
            if metaCont is not None:
                #dans le cas ou le string n'est pas de la forme de translator
                try:
                    metaCont = ' '.join(metaCont.split())
                    arrayToCheck.append(translator.translate(metaCont,dest='en'))
                except:
                    pass
        incr = 0
        for translation in arrayToCheck:
            for word in translation.text:
                if word in power_words:
                    incr+=1
                    print(word)
        return incr
    
    def getContentInfo(self, webContent, translator,seuil_toxicite=0.5):
        dico = dict()
        arrayToCheck = []
        s = BeautifulSoup(webContent,'html.parser')

        #("----------TITRE-------------")
        for titre in s.find_all("title"):
            titreS = titre.string
            if(titreS is not None):
                try:
                    titreS = ' '.join(titreS.split())
                    arrayToCheck.append(translator.translate(titreS,dest='en'))
                except:
                    pass
        #("----------PARAGRAPHE-----------")
        for paragraph in s.find_all("p"):
            pS = paragraph.string
            if(pS is not None):
                try:
                    pS = ' '.join(pS.split())
                    arrayToCheck.append(translator.translate(pS,dest='en'))
                except:
                    pass
        incr = 0
        for translation in arrayToCheck:
            result = self.pipeline(translation.text)
            if result[0]["score"] > seuil_toxicite:
                incr+=1
        return incr

    