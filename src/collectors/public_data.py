import json
import os
import random
import requests
from pathlib import Path

BASE_URL = "https://api.odcloud.kr/api/15077093/v1/open-data-list"
SEEN_PATH = Path("data/seen_public_data.json")
ALL_CACHE_PATH = Path("data/public_data_all.json")

CATEGORIES = [
    "공공행정", "과학기술", "교통물류", "국토관리", "사회복지",
    "산업고용", "식품건강", "재난안전", "재정금융", "통일외교안보",
    "환경기상", "교육", "농축수산", "문화관광", "법률", "보건의료",
]


def get_today_category(day_of_year: int) -> str:
    return CATEGORIES[day_of_year % len(CATEGORIES)]


def _load_seen() -> dict:
    if not SEEN_PATH.exists():
        return {}
    with open(SEEN_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_seen(seen: dict) -> None:
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False)


def fetch_datasets(category: str, service_key: str, per_page: int = 300) -> list[dict]:
    params = {
        "page": 1,
        "perPage": per_page,
        "serviceKey": service_key,
        "cond[new_category_nm::EQ]": category,
    }
    resp = requests.get(BASE_URL, params=params, headers={"accept": "*/*"}, timeout=15)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    seen_ids = set()
    unique = []
    for item in data:
        lid = item.get("list_id")
        if lid and lid not in seen_ids:
            seen_ids.add(lid)
            unique.append(item)
    return unique


def pick_datasets(category: str, service_key: str, n: int = 3) -> list[dict]:
    all_datasets = fetch_datasets(category, service_key)
    seen = _load_seen()
    seen_ids = set(seen.get(category, []))

    available = [d for d in all_datasets if d.get("list_id") not in seen_ids]
    if len(available) < n:
        # 해당 카테고리 seen 초기화
        seen_ids = set()
        available = all_datasets

    picks = random.sample(available, min(n, len(available)))

    seen[category] = sorted(seen_ids | {d["list_id"] for d in picks if d.get("list_id")})
    _save_seen(seen)
    return picks


def collect(day_of_year: int) -> dict:
    category = get_today_category(day_of_year)

    if ALL_CACHE_PATH.exists():
        with open(ALL_CACHE_PATH, encoding="utf-8") as f:
            all_data = json.load(f)
        datasets = all_data.get("categories", {}).get(category, [])
    else:
        service_key = os.environ["PUBLIC_DATA_SERVICE_KEY"]
        raw = fetch_datasets(category, service_key)
        datasets = [
            {
                "title": d.get("list_title", ""),
                "desc": d.get("desc", ""),
                "org": d.get("org_nm", ""),
                "keywords": d.get("keywords", ""),
                "endpoint": d.get("end_point_url", ""),
                "list_id": d.get("list_id", ""),
            }
            for d in raw
        ]

    seen = _load_seen()
    seen_ids = set(seen.get(category, []))
    available = [d for d in datasets if d.get("list_id") not in seen_ids]
    if len(available) < 2:
        seen_ids = set()
        available = datasets

    picks = random.sample(available, min(2, len(available)))
    seen[category] = sorted(seen_ids | {d["list_id"] for d in picks if d.get("list_id")})
    _save_seen(seen)

    return {
        "category": category,
        "datasets": [
            {
                "title": d.get("title", ""),
                "desc": d.get("desc", ""),
                "org": d.get("org", ""),
                "keywords": d.get("keywords", ""),
                "endpoint": d.get("endpoint", ""),
                "list_id": d.get("list_id", ""),
                "url": (
                    f"https://www.data.go.kr/data/{d.get('list_id')}/openapi.do"
                    if d.get("list_id") else ""
                ),
            }
            for d in picks
        ],
    }
