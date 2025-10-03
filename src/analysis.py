import requests
import sqlite3
import pickle
import numpy as np
from bs4 import BeautifulSoup
from scraping import loadPages, loadSinglePage

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
import tldextract



TOXICITY_TRESHOLD = 2.5  # Un site est toxique si son score dépasse ce seuil.



def getScores(pages):
    """
    Calcule le score de toxicité d'une page en se basant sur son contenu. Plus particulièrement sur ses appels APIs.

    Args:
        page : Un dictionnaire contenant les urls et leurs contenus HTML/Javascript { url -> [page_source]} 
    
    Returns:
        Un dictionnaire contenant les urls et leurs scores. { url -> [score, from_safe] }
    """

    dico = dict()
    
    for url in pages:
        
        calls = 0
        score = 0
        
        content = pages[url]

        coefficient = 0

        # Parser tous les endroits de la page où il y a des appels API:
        soup = BeautifulSoup(content, features="lxml")

        for script in soup.find_all("script"):
            if "fetch" in script.text:
                calls += 1
            if "XMLHttpRequest" in script.text:
                calls += 1

        score = calls
        
        # Les differents criteres tels que le pagerank de l'url doivent etre placés ici je crois. 

        dico[url] = score

    return dico

def getSingleScore(page):
    """
    Calcule le score de toxicité d'une page en se basant sur son contenu. Plus particulièrement sur ses appels APIs.

    Args:
        page : Contenu d'une page web.
    
    Returns:
        Le score de toxicité de la page
    """
    calls = 0
    score = 0
    soup = BeautifulSoup(page, features="lxml")

    for script in soup.find_all("script"):
        if "fetch" in script.text:
            calls += 1
        if "XMLHttpRequest" in script.text:
            calls += 1

    score = calls

    return score

def get_api_info(url):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(), options=options)

    api_urls = []
    result = {
        "url": url,
        "api_calls": 0,
        "origins": []
    }

    try:
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, "lxml")

        script_tags = soup.find_all("script")
        for script in script_tags:
            content = script.string or ""
            found_urls = re.findall(r'(https?://[\w\.-]+)', content)
            api_urls.extend(found_urls)

    except Exception as e:
        print("Erreur lors de l'analyse :", e)
    finally:
        driver.quit()

    seen_domains = set()

    for api_url in api_urls:
        domain_info = tldextract.extract(api_url)
        domain = ".".join(part for part in [domain_info.domain, domain_info.suffix] if part)

        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            try:
                ip_lookup = requests.get(f"http://ip-api.com/json/{domain}", timeout=5).json()
                country = ip_lookup.get("country", "Unknown")
            except Exception:
                country = "Unknown"
            result["origins"].append({
                "domain": domain,
                "country": country
            })

    result["api_calls"] = len(api_urls)
    return result


def manual_classification(dataset):
    """
    Cette fonction prends en entrée un dataset de pages web et applique une analyse de la toxicité et une classification de 
    chacune des pages. La méthode de classification manuelle est utilisé (à l'aide d'un seuil de toxicitié défini).
    
    Tous les résultats sont enregistrés dans la base de donnée 'projet.db'.
    
    """
    pages = loadPages(dataset)
    print(pages)
    print("\n")
    dico = getScores(pages)
    print(dico)
    

    connection = sqlite3.connect('../dataset/bdd/projet.db')
    cursor = connection.cursor()

    for url in dico:
	
	
        try:
            
            # verifier si l'url est deja presente dans la table ALL_URL_SAFE ou ALL_URL_NOT_SAFE
            cursor.execute("SELECT COUNT(*) FROM ALL_URL_SAFE WHERE URL = ?", (url,))
            if cursor.fetchone()[0] > 0:
                print(f"{url} is already in ALL_URL_SAFE table.")
                continue  

            cursor.execute("SELECT COUNT(*) FROM ALL_URL_NOT_SAFE WHERE URL = ?", (url,))
            if cursor.fetchone()[0] > 0:
                print(f"{url} is already in ALL_URL_NOT_SAFE table.")
                continue  
	    
            # analyse de la toxicité de l'URL
            
            score = dico[url][0]
            print(url , ": ", dico[url][0])
            if score >= TOXICITY_TRESHOLD:
                print(f"{url} is dangerous with a score of {score}.\n")
                # ajout de l'url à la table ALL_URL_NOT_SAFE
                cursor.execute("INSERT INTO ALL_URL_NOT_SAFE (URL, SCORE) VALUES (?, ?)", (url, score))
                connection.commit()
            else:
                print(f"{url} is safe with a score of {score}.\n")
                cursor.execute("INSERT INTO ALL_URL_SAFE (URL, SCORE) VALUES (?, ?)", (url, score))
                connection.commit()

            # on commit après chaque insertion pour sauvegarder immediatement les changements
            #connection.commit()

        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            continue

    connection.close()


def automatic_classification(dataset):
    """
    Cette fonction prends en entrée un dataset de pages web et applique une analyse de la toxicité et une classification de 
    chacune des pages. La méthode de classification automatique est utilisé (à l'aide du classifieur présent dans 'classifier.pkl').
    
    Tous les résultats sont enregistrés dans la base de donnée 'projet.db'.
    
    """

    pages = loadPages(dataset)
    dico = getScores(pages)

    connection = sqlite3.connect('../dataset/bdd/projet.db')
    cursor = connection.cursor()

    for url in dico:

        try:

            # verifier si l'url est deja presente dans la table ALL_URL_SAFE ou ALL_URL_NOT_SAFE
            cursor.execute("SELECT COUNT(*) FROM ALL_URL_SAFE WHERE URL = ?", (url,))
            if cursor.fetchone()[0] > 0:
                print(f"{url} is already in ALL_URL_SAFE table.")
                continue  

            cursor.execute("SELECT COUNT(*) FROM ALL_URL_NOT_SAFE WHERE URL = ?", (url,))
            if cursor.fetchone()[0] > 0:
                print(f"{url} is already in ALL_URL_NOT_SAFE table.")
                continue

            page = loadSinglePage(url)
            score = getSingleScore(page)
            res = isToxic(score)

            if res == 1:
                print(f"{url} is dangerous.\n")
                # ajout de l'url à la table ALL_URL_NOT_SAFE
                cursor.execute("INSERT INTO ALL_URL_NOT_SAFE (URL, SCORE) VALUES (?, ?)", (url, score))
                connection.commit()
            
            else:
                print(f"{url} is safe.\n")
                cursor.execute("INSERT INTO ALL_URL_SAFE (URL, SCORE) VALUES (?, ?)", (url, score))
                connection.commit()

        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            continue

    connection.close()


def isToxic(score: int, filepath: str) -> int:
    """
    Cette fonction utilise le classifieur stocké dans le fichier 'classifier.pkl' afin de déterminer 
    si un score de toxictié d'une page web est classé toxique ou non.

    Args:
        url: La page à classifier.

    Returns:
        True si url est toxique, False sinon
    """

    

    x = [[score]]
    x = np.array(x)
    x.reshape(-1, 1)

    with open(filepath, 'rb') as f:
        clf = pickle.load(f)
        
        if clf.predict(x) == 0:
            print("Toxic!")
            return True
        else:
            print("Safe.")
            return False
        
if __name__ == "__main__":
    url = "https://www.unicaen.fr/"
    data = get_api_info(url)
    print(data)
