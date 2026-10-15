import requests
import pickle
import numpy as np
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
import tldextract



TOXICITY_TRESHOLD = 2.5  # Un site est toxique si son score dépasse ce seuil.

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


def isToxic(data, filepath: str) -> bool:
    """
    This function uses the classifier stored in the 'model/classifier.pkl' file to determine if data from a webcontent is toxic or not.

    Args:
        data: All data retrieved from a web page. 

    Returns:
        True if webcontent is toxic, False otherwise.
    """

    url = data[0]
    nb_api = data[1]
    nb_api_toxiques = data[2]
    country = data[3]
    webContent = data[4]
    nbPowerWord = data[5]
    mediane = data[6]
        
    toxic = data[8]
    final_score = data[9]

    x = [[nb_api],[nb_api_toxiques],[country],[webContent],[nbPowerWord],[mediane],[final_score]]
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
        

