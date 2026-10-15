from CustomProgressBar import *
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(current_dir,"../")
sys.path.insert(1,source_dir)
import DBHandler


#Constantes
URL_NOT_SAFE = ("Liste des URLs non toxiques", "ALL_URL_FINAL WHERE TOXIC=1")
URL_SAFE = ("Liste des URLs toxiques", "ALL_URL_FINAL WHERE TOXIC=0")
#Table en cours d'utilisation par la fenêtre principale

valeur_actuelle = URL_SAFE #1 : toxique, 0 : safe

dbh = DBHandler.DBHandler("../dataset/bdd/projet.db")
dbh.connect()

app = tk.Tk()
couleurs = dict()


"""
Fonction permettant de basculer entre les éléments toxiques / non toxiques
@param input : (string) "toxiques" / "non_toxiques" 
@param liste : (Treeview) la liste à mettre à jour
"""
def switch_table(input ,liste):
    #on doit changer la variable globale valeur_actuelle
    #si nous ne mettons pas "global", valeur_actuelle ne sera pas modifiée
    global valeur_actuelle
    if valeur_actuelle == input:
        #on sort de la fonction, pas besoin de remettre à jour la liste
        return None
    else:
        if input =="toxiques":
            valeur_actuelle = URL_NOT_SAFE
        else:
            valeur_actuelle = URL_SAFE        

    string = "SELECT * FROM " + valeur_actuelle[1] + ";"
    req = dbh.query(string)
    maj_liste(liste, req)

"""
Function: Order URL based on dangerousness
@param order : (string) "croissant" / "decroissant", ordre dans laquelle la liste est triée
@param table : (string) correspond à la table actuellement utilisée
@liste : (Treeview) liste dans laquelle les éléments seront affichés
La fonction appelle la fonction maj_liste qui va mettre à jour la liste avec les résultats triés
"""
def sort(order, table, liste):
    debut_requete = "SELECT * FROM " + table

    if order == "Croissant":
        res = dbh.query(debut_requete + " ORDER BY SCORE ASC;")[1]
    else:
        res = dbh.query(debut_requete + " ORDER BY SCORE DESC;")[1]
    maj_liste(liste, res)
    
"""
Fonction qui crée une nouvelle fenêtre, avec les détails d'une URL (% de dangerosité pour le moment)
@param data: un enregistrement
-> Affiche les informations de l'enregistrement
"""
def details(data):
    #Création d'une fenêtre présentant la toxicité d'une URL
    fenetre_details = tk.Toplevel(app)
    fenetre_details.config(bg = couleurs["main_frame"])
    fenetre_details.title("Détails de " + data[1])
    
    fenetre_details.geometry("1000x400")
    fenetre_details.columnconfigure(0, weight=1)
    fenetre_details.rowconfigure(0, weight=1)
    fenetre_details.wm_minsize(1000, 400)
    fenetre_details.wm_maxsize(fenetre_details.winfo_screenwidth(), fenetre_details.winfo_screenheight())

    cadre_details = ttk.Frame(fenetre_details, style='main_frame.TFrame', width=450, height=600)
    cadre_details.grid(column=0, row=0, sticky="nsew")
    cadre_details.columnconfigure(0, weight=1)
    cadre_details.rowconfigure(2, weight=1)

    titre = ttk.Label(cadre_details, text="URL : " + data[1], style = "information_petit.TLabel", padding=(0, 5))
    titre.configure(anchor="center")
    titre.grid(column=0, row=0, sticky="ew")
    
    titre2 = ttk.Label(cadre_details, text="Dangerosité", foreground="red", style= "dangerosite.TLabel")
    titre2.grid(column=0, row=1, sticky="nsew")
    titre2.configure(anchor="center")
    #Création d'un cadre contenant affichant les détails sur la dangerosité d'une URL
    cadre_stats = ttk.Frame(cadre_details, style="main_frame.TFrame")
    cadre_stats.grid(column=0, row=2, rowspan=2, sticky="swne")
    cadre_stats.place(in_=cadre_details, anchor="c", relx=.5, rely=.5)
    #Barre de progression représentant la dangerosité totale de l'URL
    progressbar = ttk.Progressbar( cadre_stats, orient='horizontal', length = 300, mode='determinate', maximum=100)
    progressbar["value"] = data[2]
    progressbar.grid(row=0, column=1 ,sticky="nsew")
    #Pourcentage correspondant à la dangerosité totale de l'URL, affiché à droite de la barre de progression
    progress_label = ttk.Label(cadre_stats, text=str(data[2]) + "%")
    progress_label.grid(row=0, column=2, sticky="nsew")
    #cpb = CustomProgressBar(400, 15)
    #cpb.grid(column=0, row=1)

"""
Fonction mettant à jour la liste d'URL affichées, en créant des items sur lesquels on détecte le double-clic gauche
@param liste : Elément Treeview dans lequel les items sont insérés
@param res: résultat d'une commande Sqlite
Les items sont crées dans le même ordre que le résultat res
"""
def maj_liste(liste, res):
    for child in liste.get_children():
        liste.delete(child)
    for rec in res:
        #On insère au dernier indice du Treeview l'URL d'un enregistrement rec avec comme valeur l'enregistrement 
        #même, afin de pouvoir récupérer les détails de l'URL quand celle-ci est sélectionnée.
        liste.insert("", tk.END, text=rec[1] + " | Dangerosité: " + str(rec[2]) + "%", values=rec)

def init():
	#================================================================ Création de la fenêtre principale [librairie TKinter]

	couleurs.update({"cadre" : "#6D72C3"})
	couleurs.update({"main_frame" : "#E5D4ED"})
	titre_h1 = Font(app,family="Arial Black", size=35, underline=1)
	titre_h2 = Font(app,family="Arial Black", size=21, underline=1)
	police = Font(app,family="Arial Black", size=20)
	app.config(bg = couleurs["main_frame"])

	style = ttk.Style()
	style.theme_use("default")

	style.configure("StyleDeroulant.Vertical.TScrollbar", background=couleurs["main_frame"], height=200)
	style.configure("bg1.TFrame", background=couleurs["cadre"])
	style.configure("main_frame.TFrame", background=couleurs["main_frame"])
	style.configure("information.TLabel", height=75, width=100, font= titre_h1, background=couleurs["cadre"], foreground="#E5D4ED")
	style.configure("information_petit.TLabel", height=35, width=100, font= police, background=couleurs["cadre"], foreground="#E5D4ED")
	style.configure("dangerosite.TLabel", height=75, width=100, font=titre_h2, background=couleurs["main_frame"])
	style.configure("nice.Treeview", fieldbackground="silver", rowheight=40)
    
	app.title("Is it toxic?")
	app.wm_maxsize(app.winfo_screenwidth(), app.winfo_screenheight())
	app.geometry("1366x768")
	app.wm_minsize(1366,768)
	app.columnconfigure(0, weight=1)
	app.rowconfigure(0, weight=1)


	#Cadre de la fenêtre principale
	main_frame = ttk.Frame(app, style="main_frame.TFrame")
	#Disposition des éléments à l'aide d'une grille
	main_frame.grid(column=0, row=0, sticky="nsew")
	main_frame.grid_rowconfigure(0, weight=1)
	main_frame.grid_columnconfigure(0, weight=1)
	main_frame.grid_columnconfigure(1, weight=1)
	main_frame.grid_rowconfigure(1, weight=1)
	main_frame.grid_rowconfigure(2, weight=1)
	main_frame.grid_rowconfigure(3, weight=1)
	#Titre indiquant si les URL visualisées sont toxiques ou non
	information_fenetre = ttk.Label(main_frame, text=valeur_actuelle[0], style="information.TLabel") 
	information_fenetre.configure(anchor="center")
	information_fenetre.grid(row=0, column=0, sticky="nsew", columnspan=2)

	#Création d'un cadre déroulant en utilisant Treeview (facile d'utilisation, et performant avec de grandes quantités de données)
	#selectmode = "browse", car nous souhaitons voir les détails d'un seul URL à la fois
	liste = ttk.Treeview(main_frame, columns=("URL", "Dangerosité"), selectmode="browse", show="", style="nice.Treeview")
	liste.tag_configure("focus", background="yellow")
	"""
	.bind() permet de lire un événement (double-clic gauche ici) et d'y attribuer une fonction de callback.
	Ici, on utilise .bind() sur la liste (Treeview), en détectant si le double-clic a été effectué sur un item de la liste.
	Pour savoir quel élément a été sélectionné, on utilise la méthode .focus() du Treeview.
	Ensuite, on appelle la fonction details avec en argument l'enregistrement correspondant à l'item sélectionné.
	"""
	liste.bind("<Double-1>", lambda e : details(liste.item(liste.focus())["values"]))
	liste.grid(column=0, row=2, columnspan=2, sticky="nsew")



	    

	#Création d'un cadre contenant 2 boutons, permettant d'afficher les URLs listés comme toxiques, et les URL listées comme non toxiques.
	frame_buttons = ttk.Frame(main_frame, height=100, style="bg1.TFrame")
	frame_buttons.grid(column=0,row=1, sticky="nsew", columnspan=2)
	frame_buttons.grid_columnconfigure(0, weight=1)
	frame_buttons.grid_rowconfigure(0, weight=1)
	frame_buttons.grid_columnconfigure(1, weight=1)
	frame_buttons.grid_rowconfigure(1, weight=1)

	bouton_toxiques = tk.Button(frame_buttons, text="URLs toxiques", command=lambda : switch_table("toxiques", liste), relief="ridge", padx=10, bg="gray16", font=police, fg="red")
	bouton_toxiques.grid(column=0, row=0, sticky="nsew")

	bouton_non_toxiques = tk.Button(frame_buttons, text="URL non toxiques", command=lambda : switch_table("non_toxiques" ,liste), relief="ridge", padx=10, bg="sea green", font=police, fg="pale green")
	bouton_non_toxiques.grid(column=1, row=0, sticky="nsew")

	#Création d'un cadre contenant des boutons de tri par ordre croissant/décroissant par rapport à la toxicité des URLs
	frame_buttons = ttk.Frame(main_frame, height=100, style="bg1.TFrame")
	frame_buttons.grid(column=0,row=3, sticky="nsew", columnspan=2)
	frame_buttons.grid_columnconfigure(0, weight=1)
	frame_buttons.grid_rowconfigure(0, weight=1)
	frame_buttons.grid_columnconfigure(1, weight=1)
	frame_buttons.grid_rowconfigure(1, weight=1)

	ascending_sort_button = tk.Button(frame_buttons, text="Tri croissant", command=lambda : sort("Croissant", valeur_actuelle[1], liste), relief="ridge", padx=10, bg="#E5D4ED", font=police, fg="#1D1128")
	ascending_sort_button.grid(column=0, row=0, sticky="nsew")

	descending_sort_button = tk.Button(frame_buttons, text="Tri décroissant", command=lambda : sort("Decroissant", valeur_actuelle[1], liste), relief="ridge", padx=10, bg="#1D1128", font=police, fg="#E5D4ED")
	descending_sort_button.grid(column=1, row=0, sticky="nsew")
    
	#initialisation de la fenêtre avec la liste des URL considérées comme toxiques
	res = dbh.query("SELECT * FROM " + valeur_actuelle[1] + ";")
	#initialisation de la liste des URL avec le résultat de la requête res
	maj_liste(liste, res)
	app.mainloop()



