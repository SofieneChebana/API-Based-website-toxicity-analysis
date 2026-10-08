from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import time
import tldextract
import requests


class APIAnalyzer:
    def __init__(self):
        self.risked_country = {"Russia", "China", "North Korea",'Unknown'}
        

        caps = DesiredCapabilities.CHROME
        caps["goog:loggingPrefs"] = {"performance": "ALL"}

        self.options = Options()
        self.options.add_argument("--headless=new")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-logging")
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--enable-unsafe-swiftshader") #ignore warnings


        self.options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        self.driver = webdriver.Chrome(service=Service(), options=self.options)

    def analyze_url(self, url):
        self.driver.get(url)
        time.sleep(5)  # Let the time top api request to be fully executed.

        logs = self.driver.get_log("performance")
        api_urls = set()
        origin_score = 0

        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if log["method"] == "Network.requestWillBeSent":
                request = log["params"]["request"]
                resource_type = log["params"].get("type", "")
                request_url = request["url"]

                if resource_type in ("XHR", "Fetch") or "/api" in request_url:
                    api_urls.add(request_url)

        
        seen_domains = set()
        for api_url in api_urls:
            domain_info = tldextract.extract(api_url)
            domain = ".".join(part for part in [domain_info.domain, domain_info.suffix] if part)

            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                try:
                    response = requests.get(f"http://ip-api.com/json/{domain}", timeout=5).json()
                    country = response.get("country", "Unknown")
                    
                    if country in self.risked_country:
                        origin_score += 1
                        
                except Exception:
                    continue

        return len(api_urls), origin_score

    def quit(self):
        self.driver.quit()

def build_dico_api(api_instance, all_urls):
    brute_results = []
    for url in all_urls:
        nb_calls, origin_score = api_instance.analyze_url(url)
        brute_results.append((url, nb_calls, origin_score))

    api_counts = [nb for (_, nb, _) in brute_results]
    min_api = min(api_counts)
    max_api = max(api_counts)
    range_api = max_api - min_api if max_api != min_api else 1

    dico_api = {}
    for url, nb_calls, origin_score in brute_results:
        normalized_api_score = (nb_calls - min_api) / range_api
        dico_api[url] = {
            "nbr_api": nb_calls,
            "origine_api": origin_score,
            "normalized_score_api": round(normalized_api_score * 100, 2),
            "origin_score_api": round(origin_score * 100, 2)
        }

    return dico_api

# Test
'''
urls = ["https://example.com", "https://www.betclic.fr", "https://www.lequipe.fr", "https://www.unicaen.fr"]
analyzer = APIAnalyzer()
dico = build_dico_api(analyzer, urls)
analyzer.quit()

for url, data in dico.items():
    print(f"{url} => Nombre API: {data['nbr_api']}, Score origine: {data['score_origine_api']}%, "
          f"Score API: {data['score_normalise_api']}%")
'''