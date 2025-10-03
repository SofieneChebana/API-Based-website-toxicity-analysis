import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
eval_dir = os.path.join(current_dir, "evaluation/")
reseau_dir = os.path.join(eval_dir, "reseau/")
parseContent_dir = os.path.join(eval_dir, "webcontents/")
sys.path.insert(0, eval_dir)
sys.path.insert(1, reseau_dir)
sys.path.insert(2, parseContent_dir)

import ParseContent
import Reseau
import Evaluation
import DBHandler
import API

from analysis import isToxic

def check(label, url):
	dbh = DBHandler.DBHandler("../dataset/bdd/projet.db")
	dbh.connecter()
	
	
	rx = Reseau.Reseau()
	pc = ParseContent.ParseContent()
	api = API.APIAnalyzer()
	eval = Evaluation.Evaluation(pc,api,rx)
	res = eval.evaluate_one_url(url)[0]
	url = res[0]
	nb_api = res[1]
	nb_api_toxiques = res[2]
	country = res[3]
	webContent = res[4]
	nbPowerWord = res[5]
	mediane = res[6]
	
	toxic = res[8]
	score_final = res[9]
	
	if isToxic(score_final, "classifier.pkl"):
		label['text'] = "This page is toxic."
		label.config(fg = "red")
		if dbh.requete("SELECT COUNT(*) FROM ALL_URL_FINAL WHERE URL = ?", (url,) ) == 0:
			dbh.requete("INSERT OR IGNORE INTO ALL_URL_FINAL (URL,NB_API,NB_ORIGIN_API,COUNTRY,NB_TOXIC_WEBCONTENT,NB_POWER_WORD,PAGERANK,LINKFARM,TOXIC,SCORE) VALUES(?,?,?,?,?,?,?,?,?,?)",(url,nb_api,nb_api_toxiques, country, webContent,nbPowerWord,mediane, 0, toxic, score_final))
		
	
	else:
		label['text'] = "This page is safe."
		label.config(fg = "green")
		if dbh.requete("SELECT COUNT(*) FROM ALL_URL_FINAL WHERE URL = ?", (url,) ) == 0:
			dbh.requete("INSERT INTO ALL_URL_SAFE (URL, SCORE) VALUES (?, ?)", (url, score) )
			
	dbh.deconnecter()
	

def init():
    
    app = tk.Tk()
    style = ttk.Style()
    style.theme_use("default")

    app.title("Is it toxic?")
    app.wm_maxsize(app.winfo_screenwidth(), app.winfo_screenheight())
    app.geometry("500x200")
    app.wm_minsize(500,200)
    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)

    T = tk.Text(app, height = 2, width = 52)
    
    label = tk.Label(app, text="")
    
    b = tk.Button(app, text = "Check", command= lambda: check(label, T.get("1.0", 'end-1c') ) )

    T.pack()
    b.pack()
    label.pack()
    app.mainloop()
    
init()
    


