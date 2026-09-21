# Agent-skills

Repo chứa các **Agent Skills** dùng với [Antigravity IDE](https://antigravity.dev) và các scripts/tools hỗ trợ.

## Cấu trúc thư mục

```
Agent-skills/
│
├── .agents/
│   └── skills/                      # Agent Skills (tự động load bởi Antigravity IDE)
│       ├── extract-dol-vocabulary/  # Trích xuất từ vựng từ DOL English
│       │   └── SKILL.md
│       └── extract-vocabulary/      # Trích xuất từ vựng từ URL bất kỳ
│           └── SKILL.md
│
├── english/                         # Scripts & outputs liên quan đến tiếng Anh
│   ├── scripts/                     # Python scripts
│   │   ├── extract.py
│   │   ├── extract_dol.py
│   │   ├── add_examples.py
│   │   └── generate_excel.py
│   └── outputs/                     # File xuất ra (gitignored)
│
└── README.md
```

## Cách thêm Agent Skill mới

1. Tạo folder mới trong `.agents/skills/<tên-skill>/`
2. Tạo file `SKILL.md` với frontmatter YAML:
   ```yaml
   ---
   name: tên-skill
   description: Mô tả ngắn gọn về skill.
   ---
   ```
3. Antigravity IDE sẽ tự động nhận diện skill mới.

## Cách thêm domain mới (ngoài english)

Tạo folder mới cùng cấp với `english/`, ví dụ:
- `coding/` - Scripts liên quan đến lập trình
- `data/` - Scripts xử lý dữ liệu