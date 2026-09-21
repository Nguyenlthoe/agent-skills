---
name: extract-dol-vocabulary
description: Tự động trích xuất từ vựng từ trang web DOL English và phân loại ra thành 3 file Excel riêng biệt (Vocabulary, Collocation, Structure).
---

# Extract DOL English Vocabulary Skill

Kỹ năng này giúp Agent cào dữ liệu từ vựng đặc thù từ trang web DOL English (ví dụ: các bài Reading Test có liệt kê từ vựng), đồng thời sử dụng heuristic logic để phân loại chúng thành 3 nhóm: Từ đơn (Vocabulary), Cụm từ (Collocation) và Cấu trúc (Structure) rồi xuất ra 3 file Excel riêng biệt.

## Quy trình thực hiện

Khi người dùng cung cấp URL của DOL English (ví dụ: `https://tuhoc.dolenglish.vn/...`) và yêu cầu cào/phân loại từ vựng, hãy thực hiện các bước:

### 1. Phân tích cấu trúc text (Extract Text)
- Trang web của DOL English được render bằng Next.js, cách dễ nhất để lấy từ vựng là dùng `BeautifulSoup` để lấy toàn bộ text (`soup.get_text('\n', strip=True)`).
- Từ vựng luôn được hiển thị theo chuỗi 7 dòng liên tiếp có đặc điểm nhận dạng rõ ràng:
  1. `Term` (Từ vựng)
  2. `Phonetic` (Phiên âm)
  3. `(`
  4. `PartOfSpeech` (Từ loại, vd: adj, noun, verb)
  5. `).`
  6. `Meaning` (Ý nghĩa)
  7. `Example` (Ví dụ minh họa)

### 2. Phân loại theo Heuristic
Vì web không phân loại sẵn, Agent cần sử dụng thuật toán phân loại tự động dựa trên tên của `Term`:
- **Structure (Cấu trúc)**: Các term chứa chữ " a ", " b ", "someone", "something" hoặc có từ 4 âm tiết/từ trở lên (Ví dụ: `attribute A to B`).
- **Collocation (Cụm từ ghép)**: Các term chứa từ 2 đến 3 từ và không phải là Structure (Ví dụ: `depend on`, `bounty hunters`, `bird's-nest fern`).
- **Vocabulary (Từ đơn)**: Các term chỉ có chính xác 1 từ (Ví dụ: `superficial`, `feed`, `terrain`).

### 3. Chuẩn hóa Part of Speech
- Cần viết hoa toàn bộ từ loại lấy được từ dòng số 4 để đồng nhất format (Ví dụ: `adj` -> `ADJ`, `noun` -> `NOUN`, `verb` -> `VERB`).

### 4. Xuất ra các file Excel riêng biệt
- Sử dụng thư viện `pandas` để xuất ra 3 file Excel riêng:
  - `dol_vocabulary.xlsx`
  - `dol_collocation.xlsx`
  - `dol_structure.xlsx`
- Luôn kiểm tra lỗi `PermissionError`. Nếu file đang được người dùng mở, tự động thêm đuôi `_updated.xlsx` để tránh gián đoạn.

## Mã mẫu (Python Template)

```python
import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'URL_NGUOI_DUNG_CUNG_CAP'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Lấy toàn bộ text
text = soup.get_text('\n', strip=True)
lines = [line.strip() for line in text.split('\n') if line.strip()]

vocab_list, collocation_list, structure_list = [], [], []

# Trích xuất dựa trên chuỗi 7 dòng lặp lại
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
        
        # Logic Phân loại
        term_lower = term.lower()
        words = term.split()
        
        if " a " in term_lower or " b " in term_lower or "someone" in term_lower or "something" in term_lower or len(words) >= 4:
            structure_list.append(row)
        elif len(words) > 1:
            collocation_list.append(row)
        else:
            vocab_list.append(row)

# Hàm ghi Excel an toàn
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
```
