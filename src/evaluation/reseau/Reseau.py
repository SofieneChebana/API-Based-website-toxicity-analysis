import os
import sys
import networkx as nx
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import math
from operator import itemgetter

current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(current_dir,"../../")
sys.path.insert(1,source_dir)
import DBHandler


class Reseau:

    def __init__(self):
        self.G = nx.DiGraph()#Directed graph
        self.pages = []#nodes
        self.dico_pages = {}
        self.dbh = DBHandler.DBHandler("../../dataset/bdd/projet.db")
        self.dbh.connect()
        
        #self.resetALL_URL_PAGERANK()
        #time.sleep(10000)

        self.generateLink()
        self.pr = nx.pagerank(self.G,alpha=0.85)
        #print("pageRank:",pr)
        self.data = self.dicoData(self.pr)
        self.dbh.disconnect()
        
        
    def add_page(self,name):
        self.G.add_node(name)
        self.pages.append(name)

    #lien_href est une liste de string qui correspond au nom des liens accessible depuis ce site
    def add_page_href(self,name,lien_href):
        self.G.add_node(name)
        if len(lien_href)>0:
            if(lien_href[0]!=''):#dans le cas ou on a le premier lien qui vaut null faudrai pas ajouter une page
                for page in lien_href:
                    if page not in self.pages:
                        self.add_page(page)
                    self.G.add_edge(name,page)



    def getGraph(self):
        return self.G


    
    def seeGraph(self):
        print("------------------------------")
        print("graphe1")
        print("nombre Noeud: ",self.G.number_of_nodes())
        print("ma liste : ",self.pages)
        print("les Arretes: ",list(self.G.edges))

    
    
    def removeComma(self,href):
        res = href.split(',')
        return res


    
    def resetALL_URL_PAGERANK(self):
        self.dbh.query("DROP TABLE IF EXISTS ALL_URL_WITH_PAGE_RANK")
        self.dbh.query("CREATE TABLE IF NOT EXISTS ALL_URL_WITH_PAGE_RANK(ID INTEGER PRIMARY KEY,URL TEXT NOT NULL,PAGERANK REAL,LINK_FARM INTEGER,UNIQUE(URL))")



    def generateLink(self):
        url = self.dbh.query("SELECT * FROM ALL_URL;")

        for element in url:
            stringToSlice = element[3]
            liste = self.removeComma(stringToSlice)
            self.add_page_href(element[1],liste)
            self.dico_pages[element[1]] = element[2]

        #self.dbh.query("INSERT OR IGNORE INTO ALL_URL (URL,HREF) VALUES(?,?)",(url,href))
        #self.connection.commit()
        return


    
    #limite est le seuil à franchir pour detecter 
    def dicoData(self,dico,limite=None):
        result = dict()

        if limite == None:
            #print(len(self.dico_pages))
            limite=math.ceil(len(self.dico_pages)/4)#par exemple sur 40 ALL_URL cad des noeuds qui ont des outgoing links on obtient 10 éléments suspects c'est subjectif (avec 40 et /2 on obtient des résultats sur les links farms)
        setSuspect = set(dict(sorted(self.dico_pages.items(),key=itemgetter(1),reverse=True)[:limite]))#on recupère les 10 sites qui ont le plus de outgoing links
        
        parcourir = sorted(dico.items(),key=itemgetter(1)) #probablement nLogN
        i=0
        nbValeurChangé=0
        value = 0
        while(nbValeurChangé<limite and i<len(parcourir)):
            if value!=parcourir[i][1]:
                value = parcourir[i][1]
                nbValeurChangé+=1
            i+=1
        
        # print(value)
        for ele in self.dico_pages:
            isLinkFarm = 0
            if ele in setSuspect:
                #décommentez cette ligne de code pour avoir une visualisation
                #print(ele," Avec nbr de outgoing links: ",self.dico_pages[ele]," et qui vaut : ",dico[ele])
                if dico[ele] <value:
                    isLinkFarm =1
            result[ele] = (dico[ele], isLinkFarm)
            # self.dbh.query("INSERT OR IGNORE INTO ALL_URL_WITH_PAGE_RANK (URL,PAGERANK,LINK_FARM) VALUES(?,?,?)",(ele,dico[ele],isLinkFarm))
            # self.connection.commit()
        
        return result



    def getData(self):
        return self.data



    def getPageRank(self):
        return self.pr