import os
import sys
#python3 -m pip install networkx
#python3 -m pip install numpy
#python3 -m pip install scipy
#python3 -m pip install matplotlib
current_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(current_dir, "ui/" )
eval_dir = os.path.join(current_dir, "evaluation/")
reseau_dir = os.path.join(eval_dir,"reseau/")
parseContent_dir = os.path.join(eval_dir,"webcontents/")

sys.path.insert(0, module_dir)
sys.path.insert(1, eval_dir)
sys.path.insert(2,reseau_dir)
sys.path.insert(3,parseContent_dir)
import DBHandler
import Evaluation
import Reseau
import ParseContent
import API
import networkx as nx
import matplotlib.pyplot as plt
from app import init
import sqlite3
#import selenium
from analysis import manual_classification, automatic_classification, isToxic


def main():
    rx = Reseau.Reseau()
    pc = ParseContent.ParseContent()
    api = API.APIAnalyzer()

    eval = Evaluation.Evaluation(pc,api,rx)
    
    
    creationFichierGraph()

def creationFichierGraph():
    graph = Reseau.Reseau()
    nx.draw(graph.getGraph(),with_labels=False)
    plt.savefig("network_graph.png")


if __name__ == "__main__":

    main()

    print("All results have been registered in the 'projet.db' database.")

    #L'interface graphique se lance pour qu'on visualise les resultats.
    #init()
