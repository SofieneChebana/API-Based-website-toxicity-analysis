from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def loadPages(dataset):
    pages = dict()

    service = Service()
    options = Options()
    options.add_argument("--headless=new")
    block_images = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", block_images)
    driver = webdriver.Chrome(service=service, options=options)

    for url in dataset:

        try:
            driver.get(url[0])
            pages[url[0]] = driver.page_source #Tuple :(pageContent, distance from the first page of the crawling)

        except Exception as e:
            print(f"Error processing {url}: {e}")
        
        
    driver.quit()
    
    return pages

def loadSinglePage(url):
    
    page = None
    service = Service()
    options = Options()
    options.add_argument("--headless=new")
    block_images = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", block_images)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        page = driver.page_source 
        return page

    except Exception as e:
        print(f"Error processing {url}: {e}")
            
        
        
    driver.quit()
    
    return -1

