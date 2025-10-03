import sqlite3
import urllib
import urllib.response
import urllib.robotparser
import urllib.request
import time
import requests
import networkx as nx
import sys
sys.path.append('../evaluation/webcontents')
sys.path.append('../')
import ParseContent
import DBHandler
import API

from bs4 import BeautifulSoup
from googletrans import Translator

class Crawler:

    def  __init__(self,MustRefineUrl=True):
        self.G = nx.DiGraph()
        self.urlTmp = []
        self.nbPowerWord =0
        self.webContent = 0
        self.nbrApi =0
        self.originApi=0
        self.country=0
        self.MustRefineUrl = MustRefineUrl
        
        self.connection = self.connectBDD("../../dataset/bdd/UrlCrawler.db")#Connection à la bdd url(la zone ou j'entrepose les url valide que je traiterai par la suite)
        self.connection2 = self.connectBDD("../../dataset/bdd/projet.db")#Connection à la bdd
        self.cursor = self.connection.cursor()#Creation du cursor pour faire des requêtes
        self.cursor2 = self.connection2.cursor()
        self.parse = ParseContent.ParseContent(True)
        self.api = API.APIAnalyzer()
        self.translator =Translator()
        #self.cursor.execute("CREATE TABLE IF NOT EXISTS LIST_URL(URL TEXT NOT NULL,PROFONDEUR INT NOT NULL,FROM_SAFE INT NOT NULL,UNIQUE(URL))")
        #print(self.cursor.fetchall())
        #print(self.refine_Url("https://docs.python.org/3.0/library/urllib.request.html"))
        #print(self.robot_Allowed(self.refine_Url("https://docs.python.org/3.0/library/urllib.request.html")))
        
        self.launchCrawler()
        

    def launchCrawler(self):
        self.cursor.execute("Select * from LIST_URL LIMIT 1")
        #print(self.cursor.fetchall())
        url = self.cursor.fetchone()

        #self.resetListUrl()
        #time.sleep(10000)
        while(url is not None):#il reste des éléments dans la liste
            
            if(self.robot_Allowed(self.refine_Url(url[0]))):
                page = requests.get(url[0])
                print("Nouvelle Iteration")
                #renvoie un set contenant touts les liens qui partent de url
                links = self.gatherLink(page.text,url[0])
                stringLinks = self.traitementLinks(links)
                #on ajoute à la liste ALL_URL le lien avec les href valables vers lequel il pointe :
                self.nbrApi,self.originApi = self.api.analyze_url(url[0])
                self.addALL_URL(url[0],len(links),stringLinks,self.nbPowerWord,self.webContent,self.nbrApi,self.originApi,self.country)

           

            self.removeLIST_URL(url[0])
            for element in self.urlTmp:#on ajoute tout les liens trouvé dans la bdd pour pas les perdres
                self.addList_URL(element,url[1],url[2])
            
            
            del self.urlTmp[:]#on vide la liste
            self.cursor.execute("Select * from LIST_URL LIMIT 1 ")#prend le prochaine éléments de la liste
            url = self.cursor.fetchone()
            print("waiting 3s")
            time.sleep(3)#La politness qu'on respecte
        


    def gatherLink(self,webContent,url):#récupere tout les liens disponibles à partir d'ici
        SetLinks = set()
        s = BeautifulSoup(webContent,'html.parser')
        self.nbPowerWord = self.parse.nbrPowerWord(webContent,self.translator)
        self.webContent = self.parse.getContentInfo(webContent,self.translator,0.5)
        self.country = self.parse.getCountry(url)
        #ici rajouté le traitement de webcontent
        for lien in s.findAll('a'):
            
            valueTmp = lien.get('href')#ValueTmp ne vaut pas forcement http il faut le verifier
            if(valueTmp!=None):
                if len(valueTmp) >=4:#La chaine de caractère est trop petite
                    if(valueTmp[0:4] == 'http'):#La chaine de caractère n'est pas une Url de la forme http
                        if(self.MustRefineUrl):
                            valueTmp = self.refine_Url(valueTmp)
                        if(valueTmp not in SetLinks):#Permettera de faire le graph
                            SetLinks.add(valueTmp)

                        if((not self.alreadyExists(valueTmp)) and (not valueTmp in self.urlTmp) and (valueTmp!=url)):#est present ou non dans la table que l'on doit remplir ou dans les liens déja cliquable
                            self.urlTmp.append(valueTmp)
        return SetLinks
                        

                 
        #print(self.urlTmp)
    

    def removeLIST_URL(self,url):
        self.cursor.execute("DELETE FROM LIST_URL WHERE URL =?",(url,))
        self.connection.commit()
        return

    def addALL_URL(self,url,nb_OutGoing_Links,href,powerWord,webcontent,nbr_api,nbr_bad_origin,pays):
        self.cursor2.execute("INSERT OR IGNORE INTO ALL_URL (URL,NB_OUTGOING_LINKS,HREF,POWER_WORD,WEBCONTENT,NBR_API,NBR_API_BAD_ORIGIN,PAYS) VALUES(?,?,?,?,?,?,?,?)",(url,nb_OutGoing_Links,href,powerWord,webcontent,nbr_api,nbr_bad_origin,pays))
        self.connection2.commit()
        return
    
    def addList_URL(self,url,distance,safe):
        self.cursor.execute("INSERT OR IGNORE INTO LIST_URL (URL,PROFONDEUR,FROM_SAFE) VALUES(?,?,?)",(url,distance+1,safe))
        self.connection.commit()
        return

        
    def alreadyExists(self,url):#renvoi 1 si ca existe deja et 0 sinon
        self.cursor2.execute("SELECT EXISTS(SELECT * FROM ALL_URL WHERE URL = ?)",(url,))
        return self.cursor2.fetchone()[0]

    def resetListUrl(self):
        self.cursor.execute("DROP TABLE IF EXISTS LIST_URL")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS LIST_URL(URL TEXT NOT NULL,PROFONDEUR INT NOT NULL,FROM_SAFE INT NOT NULL,UNIQUE(URL))")
        self.cursor2.execute("DROP TABLE ALL_URL")
        #href TEXT est une liste de lien (j'evite d'utiliser json car ca rallonge enormément le temps de calcul) 
        self.cursor2.execute("CREATE TABLE ALL_URL(ID integer primary key,URL TEXT NOT NULL,NB_OUTGOING_LINKS INTEGER,HREF TEXT,POWER_WORD INTEGER,WEBCONTENT INTEGER ,NBR_API INTEGER,NBR_API_BAD_ORIGIN INTEGER,PAYS INTEGER,UNIQUE(URL))")

        self.cursor.execute("INSERT OR IGNORE INTO LIST_URL (URL,PROFONDEUR,FROM_SAFE) VALUES(?,?,?)",("https://www.unicaen.fr",0,0))
        self.cursor.execute("INSERT OR IGNORE INTO LIST_URL (URL,PROFONDEUR,FROM_SAFE) VALUES(?,?,?)",("https://www.lequipe.fr",0,0))
        self.cursor.execute("INSERT OR IGNORE INTO LIST_URL (URL,PROFONDEUR,FROM_SAFE) VALUES(?,?,?)",("http://government.ru/en/",0,0))
        self.connection.commit()
        self.connection2.commit()

    def connectBDD(self,url):
        connect = sqlite3.connect(url)
        return connect

    def disconnect(self):
        self.connection.close()

    def refine_Url(self,url):
        position = url.find("/",8)#je determine la position du premier / apres ceux du https://
        if position == -1:#find à rien trouvé l'url n'a donc pas de / 
            return url
        else:
            return url[0:position]

    def robot_Allowed(self,url):
        newUrl = url+"/robots.txt"
        try:
            robotFileparser = urllib.robotparser.RobotFileParser()
            robotFileparser.set_url(newUrl)
            robotFileparser.read()
            return robotFileparser.can_fetch('*',newUrl)
        except:
            print("erreur d'accès")
            return False
    #va prendre une liste de lien pour tout mettre dans un string ce qui sera plus simple à entreposer qu'un fichier json qui contient une liste de string 
    def traitementLinks(self,SetLinks):
        res = ""
        if len(SetLinks)==0:
            return res
        
        for ele in SetLinks:
            res += str(ele)
            res += ","

        return res[:-1]

        


