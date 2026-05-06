#!/usr/bin/env python3
"""모든 카테고리 공공데이터를 한 번에 fetch해서 data/public_data_all.json 에 저장.

이 파일을 git push 해두면 루틴에서 API 호출 없이 로컬 JSON만 읽어 동작.
갱신이 필요할 때만 다시 실행하면 됨 (주 1회 또는 월 1회).
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.public_data import CATEGORIES, fetch_datasets

if "PUBLIC_DATA_SERVICE_KEY" not in os.environ:
    print("PUBLIC_DATA_SERVICE_KEY 환경변수가 없습니다. source .env 후 실행하세요.")
    sys.exit(1)

service_key = os.environ["PUBLIC_DATA_SERVICE_KEY"]
all_data = {}

for i, category in enumerate(CATEGORIES, 1):
    print(f"[{i}/{len(CATEGORIES)}] {category} 수집 중...", end=" ", flush=True)
    try:
        datasets = fetch_datasets(category, service_key)
        all_data[category] = [
            {
                "title": d.get("list_title", ""),
                "desc": d.get("desc", ""),
                "org": d.get("org_nm", ""),
                "keywords": d.get("keywords", ""),
                "endpoint": d.get("end_point_url", ""),
                "list_id": d.get("list_id", ""),
            }
            for d in datasets
        ]
        print(f"{len(datasets)}개")
    except Exception as e:
        print(f"실패: {e}")
        all_data[category] = []

output = {
    "fetched_at": date.today().isoformat(),
    "categories": all_data,
}

out_path = Path("data/public_data_all.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

total = sum(len(v) for v in all_data.values())
print(f"\n완료: 총 {total}개 데이터셋 저장 → {out_path}")
print()
print("git add data/public_data_all.json && git commit -m 'data: refresh public data cache' && git push")
