---
name: tailieu-pdf-downloader
description: Tự động tải các trang tài liệu (ảnh) từ website tailieu.vn và ghép thành một file PDF hoàn chỉnh.
---

# Tải tài liệu từ tailieu.vn thành PDF

Skill này giúp bạn tải toàn bộ các trang nội dung của một tài liệu trên `tailieu.vn` mà không cần đăng nhập, sau đó tự động ghép chúng lại thành một file PDF hoàn chỉnh.

## Cách sử dụng

Khi user yêu cầu tải tài liệu từ tailieu.vn, hãy dùng `run_command` để chạy script Python:

```bash
python3 /home/nguyenlt/agent-skills/.agents/skills/tailieu-pdf-downloader/scripts/download.py "<url_tai_lieu>" -o "<ten_file_xuat.pdf>"
```

### Ví dụ

```bash
python3 /home/nguyenlt/agent-skills/.agents/skills/tailieu-pdf-downloader/scripts/download.py \
  "https://tailieu.vn/doc/tap-tai-lieu-giang-day-va-hoc-tap-nghiep-vu-su-pham-2938937.html" \
  -o "/home/nguyenlt/agent-skills/tai_lieu.pdf"
```

### Tham số

| Tham số | Mặc định | Mô tả |
|---|---|---|
| `url` | *(bắt buộc)* | Đường dẫn tài liệu trên tailieu.vn |
| `-o` / `--output` | `tai_lieu.pdf` | Tên file PDF đầu ra |
| `--timeout` | `120` | Thời gian chờ tối đa (giây) |

## Yêu cầu môi trường

Các thư viện Python cần thiết (đã cài sẵn):
- `playwright` + Chromium browser
- `requests`, `beautifulsoup4`, `Pillow`

Nếu chưa cài, chạy:
```bash
pip install playwright requests beautifulsoup4 Pillow --break-system-packages
python3 -m playwright install chromium
```

## Nguyên lý hoạt động

1. **Phân tích HTML tĩnh** — đếm số trang preview từ HTML để biết giới hạn cuộn
2. **Mở Playwright (Chromium headless)** — render trang đầy đủ với JavaScript
3. **Ẩn header/sticky elements** — inject JS để ẩn header sticky, mobile menu, popup ngay từ đầu và sau mỗi lần cuộn
4. **Cuộn có giới hạn** — cuộn tối đa `num_pages × 3` lần để trigger lazy-load, tránh vòng lặp vô hạn
5. **Chụp từng trang** — dùng `element.screenshot()` để chụp chính xác từng `.page-wrapper`, không bị header che
6. **Ghép thành PDF** — dùng Pillow để ghép tất cả ảnh thành 1 file PDF

## Lưu ý

- Tailieu.vn chỉ cho xem **preview** một số trang nhất định mà không cần đăng nhập. Script chỉ tải được đúng số trang đó.
- File ảnh nền `bg*.png` trên CDN là **trang trắng** (chỉ là background), nội dung thật được render bằng HTML/CSS overlay — vì vậy cần dùng browser để render.


# Tải tài liệu từ tailieu.vn thành PDF

Skill này giúp bạn tải toàn bộ các trang nội dung (định dạng ảnh) của một tài liệu trên trang `tailieu.vn` mà không cần đăng nhập, sau đó tự động ghép chúng lại thành một file PDF hoàn chỉnh.

## Cách sử dụng

Khi user yêu cầu tải tài liệu từ tailieu.vn, hãy sử dụng công cụ `run_command` để chạy đoạn script Python được cung cấp trong skill này.

### Lệnh chạy script

```bash
python3 /home/nguyenlt/agent-skills/.agents/skills/tailieu-pdf-downloader/scripts/download.py "<url_tai_lieu>" -o "<ten_file_xuat.pdf>"
```

### Ví dụ
User yêu cầu: "Hãy tải cho tôi tài liệu này: https://tailieu.vn/doc/tap-tai-lieu-giang-day-va-hoc-tap-nghiep-vu-su-pham-2938937.html"

Bạn (Agent) sẽ gọi lệnh sau:
```bash
python3 /home/nguyenlt/agent-skills/.agents/skills/tailieu-pdf-downloader/scripts/download.py "https://tailieu.vn/doc/tap-tai-lieu-giang-day-va-hoc-tap-nghiep-vu-su-pham-2938937.html" -o "/home/nguyenlt/agent-skills/tai_lieu_nghiep_vu_su_pham.pdf"
```

## Yêu cầu môi trường
Script yêu cầu các thư viện Python sau:
- `requests`
- `beautifulsoup4`
- `Pillow`

Nếu hệ thống báo thiếu thư viện, hãy dùng lệnh `pip install requests beautifulsoup4 Pillow` trước khi chạy script.

## Nguyên lý hoạt động
1. Đọc nội dung HTML từ URL trang chi tiết tài liệu.
2. Tìm tất cả các thẻ `<img>` có chứa đường dẫn đến CDN của tailieu.vn (`cdn.tailieu.vn/files/html`) và có tên dạng `bg1.png`, `bg2.png`...
3. Tải tất cả các ảnh này về bộ nhớ (RAM).
4. Sử dụng thư viện `Pillow` để ghép các ảnh này lại và lưu thành 1 file PDF duy nhất.
