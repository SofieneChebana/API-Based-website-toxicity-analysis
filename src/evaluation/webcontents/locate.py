import socket
import geocoder
from urllib.parse import urlparse


"""
Fonction renvoyant l'adresse IP correspondant à une URL.
Utilise la fonction getaddrinfo de la librairie socket.
@param url : (chaîne de caractères) représentant une URL
@return : (chaîne de caractères) l'adresse IP correspondant à l'URL ou bien -1 si aucune adresse IP a été trouvée.
"""
def get_ip_from_url(url):
    u = urlparse(url)
    normalised_url = u.hostname 
    ip = None
    try : 
        ip = str(socket.getaddrinfo(normalised_url, 80)[0][4][0])
        return ip
    except:
        print("IP address was not fetched by the system")
    return -1

"""
Fonction retournant le pays de laquelle provient l'adresse IP.
Utilise la librairie geocoder.
@param ip : (chaîne de caractères) représentant une adresse IP.
@return : (chaîne de caractères) le pays d'où provient l'adresse IP ou bien -1 si aucun pays détecté.
"""
def get_country(url):
    ip = get_ip_from_url(url)
    if ip == -1:
        return None
    return geocoder.ip(ip).country

"""
Fonction retournant la ville de laquelle provient l'adresse IP.
Ulise la librairie geocoder.
@param ip : (chaîne de caractères) représentant une adresse IP.
@return : (chaîne de caractères) la ville d'où provient l'adresse IP ou bien -1 si aucune ville détectée.
"""
def get_city(url):
    ip = get_ip_from_url(url)
    if ip == -1:
        return None
    return geocoder.ip(ip).city

def get_map(ip):

    geocoder.mapbox(ip)

#############################TESTS des fonctions de géolocalisation
"""
url_test = "https://www.lequipe.fr/"
print("\nURL : ", url_test, "\n")
ip_info = get_ip_from_url(url_test)
print("IP : ", ip_info, "\n")
print("Pays : ", get_country(url_test))

TESTS = ["lequipe.fr", 
         "www.lequipe.fr",
         "bet365.com", 
         "www.government.ru", 
         "fmprc.gov.cn", 
         "www.youtube.com", 
         "youtube.com", 
         "kestas.kuliukas.com", 
         "gist.github.com", 
         "www.partitionwizard.com"]
"""

def tests_url(URLS):
    for url in URLS:
        print("\nURL : ", url, "\n")
        ip_info = get_ip_from_url(url)
        print("IP : ", ip_info, "\n")
        pays = get_country(ip_info(url))
        print("Pays : ", pays)
        if pays == "Pays inconnu" or pays == "Erreur lors de la requête":
            print("Site potentiellement dangereux, pays inconnu")
            #get_map(ip_info)
    print("\nVille: ", get_city(url)) 

#tests_url(TESTS)