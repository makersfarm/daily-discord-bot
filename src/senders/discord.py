import os
import time
import requests

EMBED_LIMIT = 4000


def _format_pub_header(pub_data: dict) -> str:
    return f"**분야: {pub_data['category']}**"


def _format_hub_header(hub_data: dict) -> str:
    return (
        f"**{hub_data['title']}**\n"
        f"분야: {hub_data['field']} | 유형: {hub_data['type']} | {hub_data['year']}년 구축\n"
        f"🔗 [데이터셋 보기]({hub_data['url']})"
    )


def _chunk_by_separator(text: str, limit: int = EMBED_LIMIT, sep: str = "\n---\n") -> list[str]:
    parts = text.split(sep)
    chunks: list[str] = []
    cur = ""
    for p in parts:
        candidate = (cur + sep + p) if cur else p
        if len(candidate) <= limit:
            cur = candidate
        else:
            if cur:
                chunks.append(cur)
            # 단일 파트가 limit을 넘으면 그대로 자름 (드문 케이스)
            if len(p) > limit:
                for i in range(0, len(p), limit):
                    chunks.append(p[i:i + limit])
                cur = ""
            else:
                cur = p
    if cur:
        chunks.append(cur)
    return chunks or [""]


def _make_embed(title_base: str, desc: str, color: int, idx: int, total: int) -> dict:
    suffix = f" ({idx + 1}/{total})" if total > 1 else ""
    return {"title": title_base + suffix, "description": desc, "color": color}


def build_payloads(pub_data: dict, hub_data: dict, public_idea: str, aihub_idea: str) -> list[dict]:
    pub_full = _format_pub_header(pub_data) + "\n\n" + public_idea
    hub_full = _format_hub_header(hub_data) + "\n\n" + aihub_idea

    pub_chunks = _chunk_by_separator(pub_full)
    hub_chunks = _chunk_by_separator(hub_full)

    pub_embeds = [
        _make_embed("📊 오늘의 공공데이터 아이디어", c, 0x3498DB, i, len(pub_chunks))
        for i, c in enumerate(pub_chunks)
    ]
    hub_embeds = [
        _make_embed("🤖 오늘의 AI Hub 아이디어", c, 0x2ECC71, i, len(hub_chunks))
        for i, c in enumerate(hub_chunks)
    ]

    if len(pub_chunks) == 1 and len(hub_chunks) == 1:
        return [{"embeds": pub_embeds + hub_embeds}]
    return [{"embeds": [e]} for e in pub_embeds + hub_embeds]


def build_payload(pub_data: dict, hub_data: dict, public_idea: str, aihub_idea: str) -> dict:
    payloads = build_payloads(pub_data, hub_data, public_idea, aihub_idea)
    return payloads[0] if len(payloads) == 1 else {"payloads": payloads}


def send(pub_data: dict, hub_data: dict, public_idea: str, aihub_idea: str) -> None:
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    payloads = build_payloads(pub_data, hub_data, public_idea, aihub_idea)
    for i, p in enumerate(payloads):
        if i > 0:
            time.sleep(0.5)
        resp = requests.post(webhook_url, json=p, timeout=10)
        resp.raise_for_status()
