# -*- coding: utf-8 -*-
"""
CSV를 읽어 '강원' 축제만 대상으로 아래 폴더 구조를 자동 생성합니다.

<생성 구조>
ROOT_DIR / 2025 / 강원 / <축제명_언더바변환> / (카드뉴스, 포스터)

✅ 사용 전 아래 4가지만 수정하세요.
1) PATH_TO_CSV : 2025.csv의 절대경로
2) ROOT_DIR    : 생성 시작 루트(예: D:\\홍보물, /Users/you/홍보물)
3) YEAR        : 2025 등
4) REGION      : '강원' (다른 지역으로 바꿀 수 있음)

실행 방법(Windows):
  - 파이썬 설치 후, 터미널(명령 프롬프트)에서:
    python make_festival_folders.py

macOS/Linux도 동일하게 실행 가능합니다.
"""
import csv
import sys
import re
from pathlib import Path
from typing import List

# === 사용자 설정 ===
PATH_TO_CSV = r"C:\\workspace\\uv_festival\\csv\\2025.csv"   # <-- CSV 파일 경로로 바꾸세요
ROOT_DIR    = r"C:\\홍보물"             # <-- 루트 폴더 경로로 바꾸세요
YEAR        = 2025
REGION      = "세종"
SUBFOLDERS  = ["카드뉴스", "포스터"]    # 필요시 수정

# === 열 이름 자동 감지 ===
WIDE_COL_CANDIDATES = ["광역자치단체명", "광역자치단체", "광역", "시도", "시·도", "시도명"]
FEST_COL_CANDIDATES = ["축제명", "행사명", "축제 이름", "행사 이름", "축제명칭", "축제", "행사"]

ILLEGAL = r'[<>:"/\\|?*]'  # Windows 금지 문자
def sanitize(name: str) -> str:
    # 1) 앞뒤 공백 제거  2) 공백 → 언더바  3) 금지문자 제거  4) 중복 언더바 정리
    s = (name or "").strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(ILLEGAL, "", s)
    s = re.sub(r"_+", "_", s)
    return s

def find_header(headers: List[str], candidates: List[str]) -> str:
    for c in candidates:
        if c in headers:
            return c
    # 느슨한 탐색: '축제' 또는 '행사' 단어가 들어간 열
    for h in headers:
        if any(k in h for k in ["축제", "행사"]):
            return h
    return ""

def main():
    csv_path = Path(PATH_TO_CSV)
    if not csv_path.exists():
        print(f"[오류] CSV 파일을 찾을 수 없습니다: {csv_path}")
        sys.exit(1)

    root = Path(ROOT_DIR)
    base = root / str(YEAR) / REGION
    base.mkdir(parents=True, exist_ok=True)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        wide_col = find_header(headers, WIDE_COL_CANDIDATES)
        fest_col = find_header(headers, FEST_COL_CANDIDATES)

        if not wide_col or not fest_col:
            print("[오류] 열 이름을 찾지 못했습니다.")
            print("  감지된 헤더:", headers)
            print("  광역 후보:", WIDE_COL_CANDIDATES)
            print("  축제명 후보:", FEST_COL_CANDIDATES)
            sys.exit(1)

        created = 0
        skipped = 0
        seen = set()
        log_rows = []

        for row in reader:
            if (row.get(wide_col) or "").strip() != REGION:
                continue

            fest_raw = (row.get(fest_col) or "").strip()
            if not fest_raw:
                skipped += 1
                continue

            folder_name = sanitize(fest_raw)  # "띄어쓰기 → 언더바" 규칙
            # 중복 폴더명 방지
            unique_name = folder_name
            suffix = 1
            while (base / unique_name).exists() or unique_name in seen:
                suffix += 1
                unique_name = f"{folder_name}_{suffix}"
            seen.add(unique_name)

            fest_dir = base / unique_name
            fest_dir.mkdir(parents=True, exist_ok=True)
            # 하위 폴더
            for sub in SUBFOLDERS:
                (fest_dir / sub).mkdir(exist_ok=True)

            created += 1
            log_rows.append({"광역": REGION, "축제명": fest_raw, "폴더명": unique_name, "경로": str(fest_dir)})

    # 로그 저장
    log_path = base / f"{REGION}_축제폴더_생성로그.csv"
    with log_path.open("w", encoding="utf-8-sig", newline="") as wf:
        writer = csv.DictWriter(wf, fieldnames=["광역", "축제명", "폴더명", "경로"])
        writer.writeheader()
        writer.writerows(log_rows)

    print(f"[완료] 생성된 축제 폴더: {created}개  (건너뜀: {skipped}개)")
    print(f"[기준 경로] {base}")
    print(f"[로그 파일] {log_path}")

if __name__ == "__main__":
    main()
