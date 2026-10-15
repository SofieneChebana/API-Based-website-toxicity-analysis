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
	dbh.connect()
	
	
	rx = Reseau.Reseau()
	pc = ParseContent.ParseContent()
	api = API.APIAnalyzer()
	eval = Evaluation.Evaluation(pc,api,rx)
	data = eval.evaluate_one_url(url)[0]
	url = data[0]
	nb_api = data[1]
	nb_api_toxiques = data[2]
	country = data[3]
	webContent = data[4]
	nbPowerWord = data[5]
	mediane = data[6]
	
	toxic = data[8]
	final_score = data[9]

	print("Preprocess done.")
	
	if isToxic(data, "model/classifier.pkl"):
		label['text'] = "This page is toxic. \n Final score : "+ final_score
		label.config(fg = "red")
		if dbh.query("SELECT COUNT(*) FROM ALL_URL_FINAL WHERE URL = ?", (url,) ) == 0:
			dbh.query("INSERT OR IGNORE INTO ALL_URL_FINAL (URL,NB_API,NB_ORIGIN_API,COUNTRY,NB_TOXIC_WEBCONTENT,NB_POWER_WORD,PAGERANK,LINKFARM,TOXIC,SCORE) VALUES(?,?,?,?,?,?,?,?,?,?)",(url,nb_api,nb_api_toxiques, country, webContent,nbPowerWord,mediane, 0, toxic, final_score))
		
	
	else:
		label['text'] = "This page is safe."
		label.config(fg = "green")
		if dbh.query("SELECT COUNT(*) FROM ALL_URL_FINAL WHERE URL = ?", (url,) ) == 0:
			dbh.query("INSERT INTO ALL_URL_SAFE (URL, SCORE) VALUES (?, ?)", (url, final_score) )
	
	dbh.disconnect()
	

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
    


