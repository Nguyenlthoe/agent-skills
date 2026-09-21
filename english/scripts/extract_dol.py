import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'https://tuhoc.dolenglish.vn/luyen-thi-ielts/ielts-online-test-tu-vung-mt-ielts-17-test-3-reading-vocab'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

text = soup.get_text('\n', strip=True)
lines = [line.strip() for line in text.split('\n') if line.strip()]

vocab_list, collocation_list, structure_list = [], [], []

for i in range(len(lines) - 6):
    if lines[i+2] == '(' and lines[i+4] == ').':
        term = lines[i]
        phonetic = lines[i+1]
        pos = lines[i+3].upper()
        meaning = lines[i+5]
        example = lines[i+6]
        
        synonyms, antonyms = [], []
        try:
            import time
            res_syn = requests.get(f"https://api.datamuse.com/words?rel_syn={term}&max=3").json()
            synonyms = [item['word'] for item in res_syn]
            res_ant = requests.get(f"https://api.datamuse.com/words?rel_ant={term}&max=3").json()
            antonyms = [item['word'] for item in res_ant]
            time.sleep(0.1)
        except:
            pass

        row = {
            'Term': term,
            'Phonetic': phonetic,
            'PartOfSpeech': pos,
            'Synonyms': ", ".join(synonyms),
            'Antonyms': ", ".join(antonyms),
            'Meaning': meaning,
            'Example': example
        }
        
        term_lower = term.lower()
        words = term.split()
        
        if " a " in term_lower or " b " in term_lower or "someone" in term_lower or "something" in term_lower or len(words) >= 4:
            structure_list.append(row)
        elif len(words) > 1:
            collocation_list.append(row)
        else:
            vocab_list.append(row)

def save_excel(data, filename):
    if not data: 
        return
    df = pd.DataFrame(data)
    try:
        df.to_excel(filename, index=False)
    except PermissionError:
        df.to_excel(filename.replace('.xlsx', '_updated.xlsx'), index=False)

save_excel(vocab_list, 'dol_vocabulary.xlsx')
save_excel(collocation_list, 'dol_collocation.xlsx')
save_excel(structure_list, 'dol_structure.xlsx')

print(f"Đã lưu {len(vocab_list)} Từ vựng, {len(collocation_list)} Collocation, {len(structure_list)} Structure.")
