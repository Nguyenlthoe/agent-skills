import requests
from bs4 import BeautifulSoup
import json
import traceback

try:
    url = 'https://vietop.edu.vn/blog/tu-vung-ve-bien/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    extracted = []
    
    for row in soup.find_all('tr'):
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 2:
            extracted.append([c.get_text().strip() for c in cells])
            
    with open('extracted.json', 'w', encoding='utf-8') as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)
except Exception as e:
    traceback.print_exc()
