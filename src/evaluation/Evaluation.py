import sqlite3
import math
from operator import itemgetter
import DBHandler
import evaluation.reseau.Reseau as Reseau
import evaluation.webcontents.ParseContent as ParseContent
import requests
import numpy as np
from bs4 import BeautifulSoup
from googletrans import Translator
import API

class Evaluation:

    def __init__(self,parseContent,api, reseau = None, seuil = 0.50):
        self.reseau = reseau
        self.parseContent = parseContent
        self.api = api
        self.seuil = seuil
        self.dbh = DBHandler.DBHandler("../dataset/bdd/projet.db")
        self.dbh.connecter()
        
        if self.reseau == None:
            pass
        else:
            self.getApiDico_from_Crawler()
            self.evaluate_all_url()
        

    def allToURL_FINAL(self, dico, limit=None):
        return None
    
    def getApiDico_from_Crawler(self):
        result = {}
        command ,listeOfUrl=self.dbh.requete("Select * from ALL_URL;")
        for link in listeOfUrl:
            result[link[1]] = (link[6],link[7])

        return result

    """
    Fonction qui évalue tous les liens crawlés.
    @param percentage_nb_api : pourcentage de dangerosité lié au nombre d'appels API
    @param percentage_origin_api : pourcentage de dangerosité lié à l'origine des API
    @param percentagee_country : pourcentage de dangerosité lié à l'endroit où le site web est hébergé
    @param percentage_webcontent : pourcentage de dangerosité lié au contenu du site web
    @param percentage_power_word : pourcentage de dangerosité lié aux mots "attirants"
    @param percentage_page_rank : pourcentage de dangerosité lié au PageRank
    @param percentage_link_farm : pourcentage de dangerosité lié à une ferme de liens

    
    La méthode a forcément un pagerank
    
    """
    def evaluate_all_url(self, percentage_nb_api=30, percentage_origin_api=100, percentage_country=100, percentage_webcontent=30, percentage_power_word=10, percentage_page_rank=5, percentage_link_farm=45):
        self.reset_ALL_URL()
        dico_Api = self.getApiDico_from_Crawler()
        dico_page_rank = self.reseau.getData()
        dico_webcontent = self.parseContent.getDicoData()
        dico_country = self.parseContent.dicoCountry()
        #API
        #print(dico_Api)
        min_Api = min(valeur[0]for valeur in dico_Api.values())
        max_Api = max(valeur[0]for valeur in dico_Api.values())
        min_Api_Origin = min(valeur[1]for valeur in dico_Api.values())
        max_Api_Origin = max(valeur[1]for valeur in dico_Api.values())
        #webContent
        min_powerWord = min(valeur[0] for valeur in dico_webcontent.values())
        min_webContent= min(valeur[1] for valeur in dico_webcontent.values())
        max_PowerWord= max(valeur[0] for valeur in dico_webcontent.values())
        max_webContent=max(valeur[1] for valeur in dico_webcontent.values())
        #Normalisation Robuste du page rank:
        sortedDictio = sorted(self.reseau.getPageRank().values())
        mediane = np.median(sortedDictio)
        indexMedian = len(sortedDictio)//2
        quartile1 = np.median(sortedDictio[:indexMedian])
        quartile3= np.median(sortedDictio[indexMedian:])
        min_robuste =  (min(self.reseau.getPageRank().values())- mediane)/(quartile3-quartile1)
        max_robuste =   (max(self.reseau.getPageRank().values())- mediane)/(quartile3-quartile1)
        #---------------------------------------------------------------------------------------#
        
        for element in dico_page_rank:
            #score_final A COMPLETER
            score_WebContent = self.calculScoreDeuxiemeIndice(element,dico_webcontent,min_webContent,max_webContent,percentage_webcontent)
            score_powerWord = self.calculScorePremierIndice(element,dico_webcontent,min_powerWord,max_PowerWord,percentage_power_word)
            score_pagerank = self.calculScorePageRank(element,dico_page_rank,mediane,quartile1,quartile3,min_robuste,max_robuste,percentage_page_rank)
            score_nb_toxic_api = self.calculScoreDeuxiemeIndice(element,dico_Api,min_Api_Origin,max_Api_Origin,percentage_origin_api)#(100 - dico_Api[element]['score_origine_api'])
            score_nb_api =self.calculScorePremierIndice(element,dico_Api,min_Api,max_Api,percentage_nb_api) #self.calculScoreNbrApi(dico_Api[element]['score_normalise_api'])
            score_country  = dico_country[element] * (percentage_country/100)
            score_final = score_pagerank + score_powerWord + score_WebContent+score_nb_toxic_api+score_nb_api + score_country
            #si la page est une linkfarm, on ajoute le pourcentage de dangerosité de linkfarm
            if(dico_page_rank[element][1]==1):
                score_final += (percentage_link_farm/100)
            
            score_final=score_final/100
            toxic = 1 if score_final > self.seuil else 0
            # print(f"element : {element}")
            # print(f"Score final :{score_final}")
            # print(f"Toxic: {toxic}")
            self.dbh.requete("INSERT OR IGNORE INTO ALL_URL_FINAL (URL,NB_API,NB_ORIGIN_API,COUNTRY,NB_TOXIC_WEBCONTENT,NB_POWER_WORD,PAGERANK,LINKFARM,TOXIC,SCORE) VALUES(?,?,?,?,?,?,?,?,?,?)",(element,dico_Api[element][0],dico_Api[element][1], dico_country[element], dico_webcontent[element][1],dico_webcontent[element][0],dico_page_rank[element][0], dico_page_rank[element][1],toxic,score_final) )
            #print(element , " : PageRank: ", dico_page_rank[element][0], " \nScore Pr: ", score_pagerank)
        return self.dbh.requete("SELECT SCORE, TOXIC FROM ALL_URL_FINAL")[1]
    

    """
    Fonction qui analyse une seule URL. On ne peut pas calculer le PageRank du site car on n'a pas son graphe, donc on attribue un PageRank qui vaut la médiane pour ne pas avoir d'incidence sur la classification.
    La valeur du linkfarm est par défaut 0.
    @param url : l'url à analyser
    @param percentage... : "poids" de chaque critère dans le calcul de toxicité
    """
    def evaluate_one_url(self, url, percentage_nb_api=10, percentage_origin_api=10, percentage_country=5, percentage_webcontent=15, percentage_power_word=10, percentage_page_rank=5, percentage_link_farm=45):
        page = requests.get(url)
        s = BeautifulSoup(page.text,'html.parser')
        translator = Translator()
        nbPowerWord = self.parseContent.nbrPowerWord(page.text,translator)
        webContent = self.parseContent.getContentInfo(page.text,translator,0.5)
        country = self.parseContent.getCountry(url)
        nb_api, nb_api_toxiques = self.api.analyze_url(url)
        dico_api = self.getApiDico_from_Crawler()
        dico_webcontent = self.parseContent.getDicoData()
        dico_country = self.parseContent.dicoCountry()
        sorted_dict = sorted(self.reseau.getPageRank().values())
        mediane = np.median(sorted_dict)

        #API
        #print(dico_Api)
        min_Api = min(valeur[0]for valeur in dico_api.values())
        max_Api = max(valeur[0]for valeur in dico_api.values())
        min_Api_Origin = min(valeur[1]for valeur in dico_api.values())
        max_Api_Origin = max(valeur[1]for valeur in dico_api.values())
        #webContent
        min_powerWord = min(valeur[0] for valeur in dico_webcontent.values())
        min_webContent= min(valeur[1] for valeur in dico_webcontent.values())
        max_PowerWord= max(valeur[0] for valeur in dico_webcontent.values())
        max_webContent=max(valeur[1] for valeur in dico_webcontent.values())
        
        

        score_WebContent = self.calculScorePremierIndice(url,dico_webcontent,min_webContent,max_webContent,percentage_webcontent, webContent)
        score_powerWord = self.calculScorePremierIndice(url,dico_webcontent,min_powerWord,max_PowerWord,percentage_power_word, nbPowerWord)
        score_pagerank = mediane
        score_nb_toxic_api = self.calculScorePremierIndice(url,dico_api,min_Api_Origin,max_Api_Origin,percentage_origin_api,nb_api_toxiques)#(100 - dico_api[element]['score_origine_api'])
        score_nb_api =self.calculScorePremierIndice(url,dico_api,min_Api,max_Api,percentage_nb_api, nb_api) #self.calculScoreNbrApi(dico_api[element]['score_normalise_api'])
        score_country  = country * (percentage_country/100)
        score_final = score_pagerank + score_powerWord + score_WebContent+score_nb_toxic_api+score_nb_api + score_country
        score_final=score_final/100
        toxic = 1 if score_final > self.seuil else 0
        self.dbh.requete("INSERT OR IGNORE INTO ALL_URL_FINAL (URL,NB_API,NB_ORIGIN_API,COUNTRY,NB_TOXIC_WEBCONTENT,NB_POWER_WORD,PAGERANK,LINKFARM,TOXIC,SCORE) VALUES(?,?,?,?,?,?,?,?,?,?)",(url,nb_api,nb_api_toxiques, country, webContent,nbPowerWord,mediane, 0, toxic, score_final))
        return self.dbh.requete("SELECT * FROM ALL_URL_FINAL WHERE URL=?",(url,))[1]







    def calculScorePageRank(self,element,dico_page_rank,mediane,quartile1,quartile3,min_robuste,max_robuste,percentage_page_rank):
        valeur_normalisee_robuste = (dico_page_rank[element][0] - mediane)/(quartile3-quartile1)
        valeur_normalisee_linaire = ((valeur_normalisee_robuste-min_robuste)/(max_robuste-min_robuste))*100
        score_pagerank = (100 - valeur_normalisee_linaire) * (percentage_page_rank/100) 
        return score_pagerank

    def calculScorePremierIndice(self,element,dico,min,max,percentage_power_word, value=None):
        valeur_normalisee = 0
        if max == 0:
            return 0
        if value == None:
            valeur_normalisee = ((dico[element][0]-min)/(max-min))*100
        else:
            valeur_normalisee = ((value - min)/max-min)*100
        
        score_powerWord = (valeur_normalisee)*(percentage_power_word/100)
        return score_powerWord
    
    def calculScoreDeuxiemeIndice(self,element,dico,min,max,percentage):
        if max ==0:
            return 0
        valeur_normalisee = ((dico[element][1]-min)/(max-min))*100
        score_powerWord = (valeur_normalisee)*(percentage/100)
        return score_powerWord
    
    
    #pour tester
    def reset_ALL_URL(self):
        self.dbh.requete("DROP TABLE ALL_URL_FINAL;")
        self.dbh.requete("CREATE TABLE ALL_URL_FINAL(ID INTEGER PRIMARY KEY AUTOINCREMENT,URL TEXT NOT NULL,NB_API INTEGER NOT NULL,NB_ORIGIN_API INTEGER,COUNTRY INTEGER,NB_TOXIC_WEBCONTENT INTEGER NOT NULL,NB_POWER_WORD INTEGER NOT NULL,PAGERANK REAL,LINKFARM INTEGER,TOXIC INTEGER NOT NULL,SCORE REAL NOT NULL, UNIQUE(URL));")
        #self.dbh.deconnecter()
