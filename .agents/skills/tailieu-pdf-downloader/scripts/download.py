#!/usr/bin/env python3
"""
Tải tài liệu từ tailieu.vn thành PDF.

Chiến lược:
  1. Gọi API để lấy thông tin tài liệu + link PDF gốc trên CDN
  2. Download thẳng file PDF (nếu public)
  3. Fallback: dùng Playwright render từng trang rồi ghép PDF

Cách dùng:
    python3 download.py <url> [-o output.pdf]
"""

import argparse
import os
import re
import sys
import time

import requests
from io import BytesIO


# ─── Helpers ──────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Referer": "https://tailieu.vn/",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}


def get_doc_slug(url: str) -> str:
    """Lấy slug từ URL. Ví dụ: tap-tai-lieu-...-2938937.html"""
    return url.rstrip("/").split("/")[-1]


def fetch_doc_info(slug: str) -> dict:
    """Gọi API để lấy thông tin tài liệu."""
    api_url = f"https://api-fe.tailieu.vn/api/document-detail-test/{slug}?offset=0&limit=5&page=1"
    r = requests.get(api_url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


# ─── Strategy 1: Download PDF gốc trực tiếp ──────────────────────────────────

def try_download_original_pdf(doc_info: dict, output_path: str) -> bool:
    """
    Thử tải file PDF gốc từ CDN.
    Trả về True nếu thành công.
    """
    sample_url = doc_info.get("sample", "")
    if not sample_url:
        return False

    print(f"   Thử tải PDF gốc: {sample_url}")
    try:
        r = requests.head(sample_url, headers=HEADERS, timeout=15, allow_redirects=True)
        if r.status_code != 200:
            print(f"   → HTTP {r.status_code}, không truy cập được.")
            return False
        content_type = r.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower():
            print(f"   → Content-Type là '{content_type}', không phải PDF.")
            return False

        size_mb = int(r.headers.get("Content-Length", 0)) / 1024 / 1024
        print(f"   → File PDF {size_mb:.1f} MB. Đang tải...")
        r2 = requests.get(sample_url, headers=HEADERS, timeout=120, stream=True)
        r2.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r2.iter_content(chunk_size=65536):
                f.write(chunk)
        actual_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"✅ Xong! File PDF: {os.path.abspath(output_path)} ({actual_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"   → Lỗi: {e}")
        return False


# ─── Strategy 2: Render từng trang bằng Playwright ───────────────────────────

def render_with_playwright(doc_url: str, doc_info: dict, output_path: str, timeout_s: int = 120):
    """
    Fallback: render từng trang bằng Playwright headless browser.
    Ẩn header/sticky, cuộn có giới hạn, chụp từng .page-wrapper.
    """
    from playwright.sync_api import sync_playwright
    from PIL import Image

    num_pages = doc_info.get("document", {}).get("document_numpage", 0)
    print(f"   Tài liệu có {num_pages} trang (sẽ tải được số trang preview cho phép).")

    print("[2/4] Đang khởi động trình duyệt (Playwright)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1200, "height": 1600},
            user_agent=HEADERS["User-Agent"],
        )

        print(f"   Mở URL: {doc_url}")
        page.goto(doc_url, wait_until="domcontentloaded", timeout=timeout_s * 1000)
        try:
            page.wait_for_selector(".page-wrapper", timeout=30000)
        except Exception:
            pass
        time.sleep(2)

        # Ẩn header và sticky elements
        _hide_sticky(page)

        # Cuộn có giới hạn để trigger lazy-load
        print("[3/4] Đang cuộn để load lazy-content...")
        max_scrolls = max(num_pages * 3, 30) if num_pages > 0 else 50
        prev_count = 0
        for i in range(max_scrolls):
            page.evaluate("window.scrollBy(0, 1600)")
            time.sleep(0.4)
            _hide_sticky(page)
            count = page.evaluate("document.querySelectorAll('.page-wrapper').length")
            if count != prev_count:
                prev_count = count

        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)
        _hide_sticky(page)
        time.sleep(1)

        page_divs = page.query_selector_all(".page-wrapper")
        total = len(page_divs)
        print(f"   Tìm thấy {total} trang để chụp.")

        if total == 0:
            print("❌ Không tìm thấy trang nào!")
            browser.close()
            sys.exit(1)

        images = []
        for i, div in enumerate(page_divs, 1):
            print(f"  Chụp trang {i}/{total}...")
            try:
                div.scroll_into_view_if_needed()
                time.sleep(0.5)
                _hide_sticky(page)
                screenshot_bytes = div.screenshot(type="png")
                img = Image.open(BytesIO(screenshot_bytes)).convert("RGB")
                images.append(img)
            except Exception as e:
                print(f"  ⚠ Lỗi trang {i}: {e}")

        browser.close()

    if not images:
        print("❌ Không chụp được trang nào!")
        sys.exit(1)

    print(f"[4/4] Đang ghép {len(images)} trang thành PDF...")
    images[0].save(
        output_path, "PDF", resolution=150.0,
        save_all=True, append_images=images[1:],
    )
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"✅ Xong! File PDF: {os.path.abspath(output_path)} ({size_mb:.1f} MB, {len(images)} trang)")


def _hide_sticky(page):
    """Inject JS để ẩn mọi header/sticky/fixed element."""
    page.evaluate("""
        () => {
            document.querySelectorAll('*').forEach(el => {
                const pos = window.getComputedStyle(el).position;
                if (pos === 'fixed' || pos === 'sticky') {
                    el.style.setProperty('display', 'none', 'important');
                }
            });
        }
    """)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Tải tài liệu từ tailieu.vn thành file PDF"
    )
    parser.add_argument("url", help="Đường dẫn tài liệu trên tailieu.vn")
    parser.add_argument("-o", "--output", default="tai_lieu.pdf", help="Tên file PDF đầu ra")
    parser.add_argument("--timeout", type=int, default=120, help="Thời gian chờ tối đa (giây)")
    args = parser.parse_args()

    slug = get_doc_slug(args.url)

    print(f"[1/4] Đang lấy thông tin tài liệu...")
    doc_info = fetch_doc_info(slug)
    doc = doc_info.get("document", {})
    print(f"   Tiêu đề : {doc.get('document_title', 'N/A')}")
    print(f"   Số trang : {doc.get('document_numpage', 'N/A')}")
    print(f"   Miễn phí: {'Có' if doc.get('document_isfree') else 'Không (chỉ xem preview)'}")

    # Thử download PDF gốc trước
    if try_download_original_pdf(doc_info, args.output):
        return

    # Fallback: dùng Playwright
    print("\n   → Dùng Playwright để render các trang preview...")
    try:
        from playwright.sync_api import sync_playwright
        from PIL import Image
    except ImportError:
        print("❌ Thiếu thư viện. Chạy: pip install playwright Pillow --break-system-packages && python3 -m playwright install chromium")
        sys.exit(1)

    render_with_playwright(args.url, doc_info, args.output, args.timeout)


if __name__ == "__main__":
    main()
