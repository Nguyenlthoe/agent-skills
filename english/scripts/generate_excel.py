import json
import pandas as pd
import requests
import time

def get_syn_ant(word):
    synonyms = []
    antonyms = []
    try:
        # Datamuse API
        res = requests.get(f"https://api.datamuse.com/words?rel_syn={word}&max=3")
        if res.status_code == 200:
            synonyms = [item['word'] for item in res.json()]
            
        res = requests.get(f"https://api.datamuse.com/words?rel_ant={word}&max=3")
        if res.status_code == 200:
            antonyms = [item['word'] for item in res.json()]
    except:
        pass
    return ", ".join(synonyms), ", ".join(antonyms)

with open('extracted.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The expected columns are: ['Term', 'Phonetic', 'PartOfSpeech', 'Synonyms', 'Antonyms', 'Meaning', 'Example']
records = []
seen = set()

for row in data:
    if len(row) >= 4:
        term, pos, phonetic, meaning = row[0], row[1], row[2], row[3]
        if term.lower() == 'từ vựng' or term == '':
            continue
        
        if term.lower() in seen:
            continue
        seen.add(term.lower())
        
        # Datamuse API works best with single words, but we'll try for phrases as well
        syn, ant = get_syn_ant(term)
        
        records.append({
            'Term': term,
            'Phonetic': phonetic,
            'PartOfSpeech': pos,
            'Synonyms': syn,
            'Antonyms': ant,
            'Meaning': meaning,
            'Example': ''
        })
        time.sleep(0.1) # Be nice to the API

df = pd.DataFrame(records)
# Save to Excel
df.to_excel('vocab_sea.xlsx', index=False)
print(f"Saved {len(records)} words to vocab_sea.xlsx")
