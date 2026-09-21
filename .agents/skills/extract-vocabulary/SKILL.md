---
name: extract-vocabulary
description: Tự động trích xuất từ vựng từ một đường link (URL) bài viết, bổ sung từ đồng nghĩa, trái nghĩa, ví dụ và xuất ra file Excel.
---

# Extract Vocabulary Skill

Kỹ năng này hướng dẫn Agent cách xử lý yêu cầu trích xuất danh sách từ vựng từ một trang web học tiếng Anh và xuất ra định dạng Excel chuẩn.

## Quy trình thực hiện

Khi người dùng cung cấp một URL và yêu cầu trích xuất từ vựng, hãy thực hiện các bước sau:

### 1. Phân tích cấu trúc HTML
- Dùng thư viện `requests` và `BeautifulSoup` trong Python để cào dữ liệu từ URL.
- Tìm các thẻ HTML chứa từ vựng (thường là các hàng trong bảng `<tr>` hoặc danh sách `<li>`).
- Bỏ qua các hàng chứa tiêu đề (ví dụ: "Từ vựng", "Ý nghĩa") hoặc các nội dung không liên quan (như đáp án bài tập).

### 2. Chuẩn hóa Part of Speech (Từ loại)
- Chuyển đổi các ký hiệu viết tắt thành từ đầy đủ theo format chuẩn:
  - `N` -> `NOUN`
  - `V` -> `VERB`
  - `Adj` -> `ADJECTIVE`
  - `Adv` -> `ADVERB`
  - `Phr` -> `Phrase`
  - `Prep` -> `PREPOSITION`
  - `Conj` -> `CONJUNCTION`
  - `Pro` -> `PRONOUN`

### 3. Tìm từ đồng nghĩa và trái nghĩa
- Sử dụng **Datamuse API** để lấy từ đồng nghĩa và trái nghĩa tự động bằng Python:
  - Đồng nghĩa: `https://api.datamuse.com/words?rel_syn={word}&max=3`
  - Trái nghĩa: `https://api.datamuse.com/words?rel_ant={word}&max=3`

### 4. Tạo ví dụ minh họa (Examples)
- Cần có ví dụ minh họa bằng tiếng Anh cho mỗi từ vựng để người dùng dễ nhớ.
- Agent có thể tự sinh ví dụ cho các từ vựng này và nhúng vào script Python dưới dạng một dictionary.

### 5. Xuất ra file Excel
- Cấu trúc các cột trong file Excel bắt buộc phải theo thứ tự sau: 
  `['Term', 'Phonetic', 'PartOfSpeech', 'Synonyms', 'Antonyms', 'Meaning', 'Example']`
- Dùng thư viện `pandas` (`to_excel`) để xuất file.
- **Xử lý lỗi cấp quyền (PermissionError)**: Nếu người dùng đang mở file Excel nên không thể ghi đè, hãy bắt lỗi `PermissionError` và tự động lưu sang một file mới có hậu tố `_updated.xlsx` (ví dụ: `vocab_updated.xlsx`).

## Mã mẫu (Python Template)

Dưới đây là cấu trúc code Python mẫu để thực hiện công việc trên:

```python
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

url = 'URL_NGUOI_DUNG_CUNG_CAP'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

records = []
seen = set()

pos_mapping = {
    'N': 'NOUN', 'V': 'VERB', 'Adj': 'ADJECTIVE',
    'Phr': 'Phrase', 'Adv': 'ADVERB', 'Prep': 'PREPOSITION',
    'Conj': 'CONJUNCTION', 'Pro': 'PRONOUN'
}

# 1. Trích xuất từ HTML
for row in soup.find_all('tr'):
    cells = row.find_all(['td', 'th'])
    if len(cells) >= 4:
        term = cells[0].get_text().strip()
        pos = cells[1].get_text().strip()
        phonetic = cells[2].get_text().strip()
        meaning = cells[3].get_text().strip()
        
        if term.lower() == 'từ vựng' or not term or term.lower() in seen:
            continue
        seen.add(term.lower())
        
        # 2. Gọi API lấy synonyms / antonyms
        synonyms, antonyms = [], []
        try:
            res_syn = requests.get(f"https://api.datamuse.com/words?rel_syn={term}&max=3").json()
            synonyms = [item['word'] for item in res_syn]
            res_ant = requests.get(f"https://api.datamuse.com/words?rel_ant={term}&max=3").json()
            antonyms = [item['word'] for item in res_ant]
        except:
            pass
            
        records.append({
            'Term': term,
            'Phonetic': phonetic,
            'PartOfSpeech': pos_mapping.get(pos, pos),
            'Synonyms': ", ".join(synonyms),
            'Antonyms': ", ".join(antonyms),
            'Meaning': meaning,
            'Example': '' # Thêm dictionary ví dụ do Agent sinh ra vào đây
        })
        time.sleep(0.1) # Tránh rate limit

df = pd.DataFrame(records)

# 3. Xuất file an toàn
output_file = 'vocab_export.xlsx'
try:
    df.to_excel(output_file, index=False)
except PermissionError:
    df.to_excel(output_file.replace('.xlsx', '_updated.xlsx'), index=False)
```
