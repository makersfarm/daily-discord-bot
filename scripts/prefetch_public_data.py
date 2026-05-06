#!/usr/bin/env python3
"""로컬에서 오늘의 공공데이터를 수집해 data/today_public.json 에 저장.

실행 후 git push 하면 루틴에서 캐시 파일을 읽어 API 호출 없이 동작.
"""
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.public_data import collect, CACHE_PATH

if "PUBLIC_DATA_SERVICE_KEY" not in os.environ:
    print("PUBLIC_DATA_SERVICE_KEY 환경변수가 없습니다. source .env 후 실행하세요.")
    sys.exit(1)

day = date.today().timetuple().tm_yday
result = collect(day)
print(f"수집 완료: {result['category']} 분야 {len(result['datasets'])}개")
print(f"저장: {CACHE_PATH}")
print()
print("다음 명령으로 루틴에 반영하세요:")
print("  git add data/today_public.json && git commit -m 'data: prefetch public data' && git push")
