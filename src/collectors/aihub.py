import json
import os
import random
import requests
from bs4 import BeautifulSoup
from datetime import date
from pathlib import Path

CATALOG_PATH = Path("data/aihub_catalog_detail.json")
SEEN_PATH = Path("data/seen_aihub.json")


def _load_catalog() -> list[dict]:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_seen() -> set[int]:
    if not SEEN_PATH.exists():
        return set()
    with open(SEEN_PATH, encoding="utf-8") as f:
        return set(json.load(f))


def _save_seen(seen: set[int]) -> None:
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f)


def _fetch_desc(dataset_id: int) -> str:
    try:
        url = f"https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn={dataset_id}"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for li in soup.find_all("li"):
            txt = li.get_text(strip=True)
            if "소개" in txt and len(txt) > 100:
                idx = txt.find("소개")
                desc = txt[idx + 2:idx + 400].strip()
                for cut in ["구축목적", "데이터 변경이력", "데이터 히스토리", "안심존"]:
                    ci = desc.find(cut)
                    if ci > 0:
                        desc = desc[:ci].strip()
                if len(desc) > 20:
                    return desc
    except Exception:
        pass
    return ""


def collect() -> dict:
    catalog = _load_catalog()
    current_year = str(date.today().year)
    catalog = [d for d in catalog if (d.get("updated") or "").startswith(current_year + "-")]
    if not catalog:
        raise RuntimeError(f"AI Hub 카탈로그에 {current_year}년 갱신 데이터셋이 없음")

    seen = _load_seen()
    available = [d for d in catalog if d["id"] not in seen]
    if not available:
        seen = set()
        available = catalog

    pick = random.choice(available)
    seen.add(pick["id"])
    _save_seen(seen)

    return {
        "id": pick["id"],
        "title": pick["title"],
        "field": pick.get("field", ""),
        "type": pick.get("type", ""),
        "tags": pick.get("tags", []),
        "year": pick.get("year", ""),
        "updated": pick.get("updated", ""),
        "downloads": pick.get("downloads", ""),
        "desc": _fetch_desc(pick["id"]),
        "url": f"https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn={pick['id']}",
    }
