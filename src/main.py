import os
import sys
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
import threading
import time
from app import init




if __name__ == "__main__":

    init()