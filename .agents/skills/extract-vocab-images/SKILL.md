---
name: extract-vocab-images
description: Trích xuất danh sách từ vựng từ các ảnh được dán vào chat, tự động tìm từ đồng nghĩa, trái nghĩa, ví dụ và xuất ra file Excel.
---

# Extract Vocabulary from Images Skill

Kỹ năng này hướng dẫn Agent cách xử lý yêu cầu khi người dùng dán (paste) hoặc tải lên một danh sách các ảnh chứa từ vựng tiếng Anh và cần xuất ra định dạng Excel chuẩn.

## Quy trình thực hiện

Khi người dùng cung cấp một hoặc nhiều hình ảnh chứa danh sách từ vựng, hãy thực hiện tuần tự các bước sau:

### 1. Đọc và trích xuất dữ liệu từ hình ảnh
- Agent sử dụng khả năng xử lý hình ảnh (vision) của mình (hoặc dùng tool `view_file` lên các đường dẫn file ảnh) để đọc toàn bộ chữ trong ảnh.
- Thu thập các thông tin có sẵn trong ảnh: **Từ vựng (Term)**, **Từ loại (PartOfSpeech)**, và **Nghĩa (Meaning)**.

### 2. Chuẩn hóa Part of Speech (Từ loại)
- Chuyển đổi các ký hiệu viết tắt trong ảnh thành từ đầy đủ theo format chuẩn:
  - `n` -> `NOUN`
  - `v` -> `VERB`
  - `adj` -> `ADJECTIVE`
  - `adv` -> `ADVERB`
  - `phr` -> `Phrase`
  - `prep` -> `PREPOSITION`
  - `conj` -> `CONJUNCTION`
  - `pro` -> `PRONOUN`

### 3. Bổ sung thông tin còn thiếu
- Sử dụng kiến thức ngôn ngữ của Agent để bổ sung các trường thông tin không có trong ảnh cho mỗi từ:
  - **Phonetic**: Phiên âm IPA chuẩn (VD: `/ækˈsɛl.ə.reɪt/`).
  - **Synonyms**: 2-3 từ đồng nghĩa (phân tách bằng dấu phẩy).
  - **Antonyms**: 2-3 từ trái nghĩa (phân tách bằng dấu phẩy).
  - **Example**: Một câu ví dụ minh họa bằng tiếng Anh ngữ cảnh thực tế.

### 4. Tạo script xuất ra file Excel
- Cấu trúc các cột trong file Excel bắt buộc phải theo thứ tự sau: 
  `['Term', 'Phonetic', 'PartOfSpeech', 'Synonyms', 'Antonyms', 'Meaning', 'Example']`
- Viết một script Python để lưu danh sách từ vựng đã trích xuất hoàn chỉnh vào file Excel tại thư mục `english/outputs/`.
- File đầu ra nên có tên phản ánh nội dung, ví dụ: `english/outputs/vocab_from_images.xlsx`.
- **Lưu ý xử lý lỗi**: Bắt lỗi `PermissionError` trong trường hợp file bị khóa (người dùng đang mở file) và tự động lưu sang tên mới có hậu tố `_updated.xlsx`.

## Mã mẫu (Python Template)

Dưới đây là cấu trúc code Python mẫu để tạo file Excel từ danh sách từ vựng do Agent trích xuất:

```python
import pandas as pd
import os

# Danh sách dữ liệu do Agent trích xuất từ ảnh và bổ sung thông tin
data = [
    # ["Term", "Phonetic", "PartOfSpeech", "Synonyms", "Antonyms", "Meaning", "Example"]
    ["accelerate", "/əkˈseləreɪt/", "VERB", "speed up, quicken", "decelerate, slow down", "tăng tốc", "The company plans to accelerate its expansion."],
    # ... Agent điền tiếp các từ khác vào đây ...
]

columns = ['Term', 'Phonetic', 'PartOfSpeech', 'Synonyms', 'Antonyms', 'Meaning', 'Example']
df = pd.DataFrame(data, columns=columns)

# Thư mục đích
output_dir = r'd:\Agent-skills\english\outputs'
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'vocab_from_images.xlsx')

# Xuất file an toàn
try:
    df.to_excel(output_file, index=False)
    print(f"✅ Đã xuất file thành công tại: {output_file}")
except PermissionError:
    alt_file = os.path.join(output_dir, 'vocab_from_images_updated.xlsx')
    df.to_excel(alt_file, index=False)
    print(f"⚠️ File cũ đang mở. Đã lưu sang file mới tại: {alt_file}")
```

### 5. Thông báo hoàn thành
- Chạy script Python để tạo file Excel.
- Phản hồi lại cho người dùng bằng cách cung cấp đường dẫn có thể click (clickable link) trỏ đến file Excel vừa tạo để người dùng dễ dàng mở lên.
