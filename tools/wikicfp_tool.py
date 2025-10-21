import requests
from bs4 import BeautifulSoup
import json
from typing import List

WIKICFP_BASE_URL = "http://www.wikicfp.com"
def search_wikicfp_tool(keyword: str, max_results: int=10, year: int = 2026, log: bool = False) -> str:
    url = f"{WIKICFP_BASE_URL}/cfp/servlet/tool.search?q={keyword}&year={year}"
    print( f"Searching WikiCFP with URL: {url}" )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    # Sempre logue as ferramentas isso irá ajudar no debug posteriormente.
    if log:
        print(f"Searching WikiCFP for keyword: {keyword}")
    # Quando estamos lidando com requisição é sempre normal acontecer erros, é boa prática usar try
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        main_content_table = soup.find_all('table')[2]
        conference_table = main_content_table.find_all("tr")[3]
        rows = conference_table.find_all('tr')
        conferences = []
        max_results = min(max_results, (len(rows)-1)//2 * 2)
        for i in range(1, max_results+1, 2):
            row = rows[i]
            cols = row.find_all('td')
            acronym_link = cols[0].find('a')
            href = f"{WIKICFP_BASE_URL}/{cols[0].find('a')['href']}"
            acronym = acronym_link.text.strip()
            full_name = cols[1].text.strip()
            if log:
                print(f"Found conference: {acronym} - {full_name} - {href}")

            next_row = rows[i+1]
            next_cols = next_row.find_all("td")
            when = next_cols[0].text.strip()
            where = next_cols[1].text.strip()
            deadline = next_cols[2].text.strip()
            if log:
                print(f"When: {when}, Where: {where}, Deadline: {deadline}")

            keywords = get_keywords(href)
            if log:
                print(f"Keywords: {keywords}")

            conferences.append({
                'acronym': acronym,
                'full_name': full_name,
                'deadline': deadline,
                'where': where,
                'when': when,
                'keywords': keywords,
                'link': href,
            })
        return conferences
    except Exception as e:
        return f"Error occured while searching WikiCFP: {str(e)}"

def get_keywords(conference_url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(conference_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        # filter by table and class class="gglu"
        main_content_table = soup.find_all('table', class_='gglu')[1]
        keywords_links = main_content_table.find_all('a')
        keywords = []
        for link in keywords_links[1:]:
            keywords.append(link.text.strip())
        return keywords

    except Exception as e:
        return [f"Error occured while fetching conference details: {str(e)}"]

if __name__ == "__main__":
    resultados = search_wikicfp_tool(["machine learning", "AI"], max_results=10, year=2025, log=True)
    print("\n--- Search Results ---")
    print(resultados)