import sqlite3
from CustomProgressBar import *
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font

#Constantes
URL_NOT_SAFE = ("Liste des URLs non toxiques", " FROM ALL_URL_FINAL WHERE TOXIC=1;")
URL_SAFE = ("Liste des URLs toxiques", " FROM ALL_URL_FINAL WHERE TOXIC=0;")
#Table en cours d'utilisation par la fenêtre principale

valeur_actuelle = URL_SAFE #1 : toxique, 0 : safe

CHEMIN_BDD_PROJET = "../dataset/bdd/projet.db"

################################################################
#Création d'une instance Tk pour l'interface graphique
app = tk.Tk()
#Styles utilisés pour l'interface graphique

#couleurs utilisées pour l'interface graphique
couleurs = dict()
couleurs.update({"cadre" : "#6D72C3"})
couleurs.update({"cadre_principal" : "#E5D4ED"})
#police d'écriture
titre_h1 = Font(app,family="Arial Black", size=35, underline=1)
titre_h2 = Font(app,family="Arial Black", size=21, underline=1)
police = Font(app,family="Arial Black", size=20)
#styles TKinter
app.config(bg = couleurs["cadre_principal"])

style = ttk.Style()
style.theme_use("default")

style.configure("StyleDeroulant.Vertical.TScrollbar", background=couleurs["cadre_principal"], height=200)
style.configure("bg1.TFrame", background=couleurs["cadre"])
style.configure("cadre_principal.TFrame", background=couleurs["cadre_principal"])
style.configure("information.TLabel", height=75, width=100, font= titre_h1, background=couleurs["cadre"], foreground="#E5D4ED")
style.configure("information_petit.TLabel", height=35, width=100, font= police, background=couleurs["cadre"], foreground="#E5D4ED")
style.configure("dangerosite.TLabel", height=75, width=100, font=titre_h2, background=couleurs["cadre_principal"])
style.configure("nice.Treeview", fieldbackground="silver", rowheight=40)

################################################################


"""
Fonction permettant de se connecter à une base de données
@param chemin : (string) le chemin à la base de données
@return : un curseur sur la base de données
"""
def connecter(chemin : str):
    curseur = None
    try:
        con = sqlite3.connect(chemin)
        curseur = con.cursor()
    except:
        print("La connection à " + chemin + " a échoué.")
    
    return curseur

#connection à la base de données projet.db 
curseur = connecter(CHEMIN_BDD_PROJET)

"""
Fonction prenant un curseur et une commande, renvoie la commande exécutée et le résultat correspondant
@commande : (string) une commande à exécuter
@return : (string, list) la commande exécutée et le résultat correspondant
"""
def requete(commande : str):
    #on doit récupérer la connection à la base de données grâce au mot-clé "global"
    global curseur
    req = None
    #Utilisation de try et except dans le cas où une commande échoue
    try:
        req = curseur.execute(commande) # query all_url
    except:
        print("La requête a échoué")
    return commande, req.fetchall()


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
    #print("valeur_actuelle: ", valeur_actuelle)
    req = requete("SELECT *" + valeur_actuelle[1])
    maj_liste(liste, req[1])

"""
Focntion: Tri les URL selon leur dangerosité
@param input : (string) "croissant" / "decroissant", ordre dans laquelle la liste est triée
@param table : (string) correspond à la table actuellement utilisée
@liste : (Treeview) liste dans laquelle les éléments seront affichés
La fonction appelle la fonction maj_liste qui va mettre à jour la liste avec les résultats triés
"""
def tri(input, table, liste):
    debut_requete = "SELECT *" + table
    if input == "Croissant":
        print("tri croissant en cours")
        res = requete(debut_requete + " ORDER BY SCORE ASC")[1]
    else:
        print("tri décroissant en cours")
        res = requete(debut_requete + " ORDER BY SCORE DESC")[1]
    maj_liste(liste, res)
    
"""
Fonction qui crée une nouvelle fenêtre, avec les détails d'une URL (% de dangerosité pour le moment)
@param data: un enregistrement
-> Affiche les informations de l'enregistrement
"""
def details(data):
    print("data URL: %s" % data[1])
    #Création d'une fenêtre présentant la toxicité d'une URL
    fenetre_details = tk.Toplevel(app)
    fenetre_details.config(bg = couleurs["cadre_principal"])
    fenetre_details.title("Détails de " + data[1])
    
    fenetre_details.geometry("1000x400")
    fenetre_details.columnconfigure(0, weight=1)
    fenetre_details.rowconfigure(0, weight=1)
    fenetre_details.wm_minsize(1000, 400)
    fenetre_details.wm_maxsize(fenetre_details.winfo_screenwidth(), fenetre_details.winfo_screenheight())

    cadre_details = ttk.Frame(fenetre_details, style='cadre_principal.TFrame', width=450, height=600)
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
    cadre_stats = ttk.Frame(cadre_details, style="cadre_principal.TFrame")
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

	app.title("Is it toxic?")
	app.wm_maxsize(app.winfo_screenwidth(), app.winfo_screenheight())
	app.geometry("1366x768")
	app.wm_minsize(1366,768)
	app.columnconfigure(0, weight=1)
	app.rowconfigure(0, weight=1)


	#Cadre de la fenêtre principale
	cadre_principal = ttk.Frame(app, style="cadre_principal.TFrame")
	#Disposition des éléments à l'aide d'une grille
	cadre_principal.grid(column=0, row=0, sticky="nsew")
	cadre_principal.grid_rowconfigure(0, weight=1)
	cadre_principal.grid_columnconfigure(0, weight=1)
	cadre_principal.grid_columnconfigure(1, weight=1)
	cadre_principal.grid_rowconfigure(1, weight=1)
	cadre_principal.grid_rowconfigure(2, weight=1)
	cadre_principal.grid_rowconfigure(3, weight=1)
	#Titre indiquant si les URL visualisées sont toxiques ou non
	information_fenetre = ttk.Label(cadre_principal, text=valeur_actuelle[0], style="information.TLabel") 
	information_fenetre.configure(anchor="center")
	information_fenetre.grid(row=0, column=0, sticky="nsew", columnspan=2)

	#Création d'un cadre déroulant en utilisant Treeview (facile d'utilisation, et performant avec de grandes quantités de données)
	#selectmode = "browse", car nous souhaitons voir les détails d'un seul URL à la fois
	liste = ttk.Treeview(cadre_principal, columns=("URL", "Dangerosité"), selectmode="browse", show="", style="nice.Treeview")
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
	frame_boutons = ttk.Frame(cadre_principal, height=100, style="bg1.TFrame")
	frame_boutons.grid(column=0,row=1, sticky="nsew", columnspan=2)
	frame_boutons.grid_columnconfigure(0, weight=1)
	frame_boutons.grid_rowconfigure(0, weight=1)
	frame_boutons.grid_columnconfigure(1, weight=1)
	frame_boutons.grid_rowconfigure(1, weight=1)

	bouton_toxiques = tk.Button(frame_boutons, text="URLs toxiques", command=lambda : switch_table("toxiques", liste), relief="ridge", padx=10, bg="gray16", font=police, fg="red")
	bouton_toxiques.grid(column=0, row=0, sticky="nsew")

	bouton_non_toxiques = tk.Button(frame_boutons, text="URL non toxiques", command=lambda : switch_table("non_toxiques" ,liste), relief="ridge", padx=10, bg="sea green", font=police, fg="pale green")
	bouton_non_toxiques.grid(column=1, row=0, sticky="nsew")

	#Création d'un cadre contenant des boutons de tri par ordre croissant/décroissant par rapport à la toxicité des URLs
	frame_boutons = ttk.Frame(cadre_principal, height=100, style="bg1.TFrame")
	frame_boutons.grid(column=0,row=3, sticky="nsew", columnspan=2)
	frame_boutons.grid_columnconfigure(0, weight=1)
	frame_boutons.grid_rowconfigure(0, weight=1)
	frame_boutons.grid_columnconfigure(1, weight=1)
	frame_boutons.grid_rowconfigure(1, weight=1)

	bouton_tri_croissant = tk.Button(frame_boutons, text="Tri croissant", command=lambda : tri("Croissant", valeur_actuelle[1], liste), relief="ridge", padx=10, bg="#E5D4ED", font=police, fg="#1D1128")
	bouton_tri_croissant.grid(column=0, row=0, sticky="nsew")

	bouton_tri_decroissant = tk.Button(frame_boutons, text="Tri décroissant", command=lambda : tri("Decroissant", valeur_actuelle[1], liste), relief="ridge", padx=10, bg="#1D1128", font=police, fg="#E5D4ED")
	bouton_tri_decroissant.grid(column=1, row=0, sticky="nsew")


	#initialisation de la fenêtre avec la liste des URL considérées comme toxiques
	res = requete("SELECT *" + valeur_actuelle[1])
	#initialisation de la liste des URL avec le résultat de la requête res
	maj_liste(liste, res[1])
	app.mainloop()



