import Crawler
import sqlite3
import atexit


def preventClosing(crawl):#permet de se deconnecter proprement de la bdd
    for ele in crawl:  
        ele.disconnect()
    
    
def main():
    crawlers = []
    crawl1 = Crawler.Crawler()
    crawlers.append(crawl1)
    atexit.register(preventClosing,crawlers)
    while(True):
        pass
    print("error :  ")

if __name__ == "__main__":
    main()