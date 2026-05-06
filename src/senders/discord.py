import os
import requests


def _format_pub_datasets(pub_data: dict) -> str:
    lines = [f"**분야: {pub_data['category']}**\n"]
    for d in pub_data["datasets"]:
        desc = d['desc'][:120] + ("…" if len(d['desc']) > 120 else "")
        keywords = f"\n  키워드: {d['keywords'][:60]}" if d.get("keywords") else ""
        lines.append(f"• **{d['title']}** ({d['org']})\n  {desc}{keywords}")
    return "\n".join(lines)


def _format_hub_dataset(hub_data: dict) -> str:
    tags = ", ".join(hub_data["tags"]) if hub_data["tags"] else "없음"
    desc = hub_data.get("desc", "")
    desc_line = f"\n{desc[:150]}{'…' if len(desc) > 150 else ''}" if desc else ""
    return (
        f"**{hub_data['title']}**\n"
        f"분야: {hub_data['field']} | 유형: {hub_data['type']} | {hub_data['year']}년 구축\n"
        f"태그: {tags}{desc_line}\n"
        f"🔗 [데이터셋 보기]({hub_data['url']})"
    )


def send(pub_data: dict, hub_data: dict, public_idea: str, aihub_idea: str) -> None:
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

    payload = {
        "embeds": [
            {
                "title": "📊 오늘의 공공데이터 아이디어",
                "description": _format_pub_datasets(pub_data) + "\n\n" + public_idea,
                "color": 0x3498DB,
            },
            {
                "title": "🤖 오늘의 AI Hub 아이디어",
                "description": _format_hub_dataset(hub_data) + "\n\n" + aihub_idea,
                "color": 0x2ECC71,
            },
        ]
    }

    resp = requests.post(webhook_url, json=payload, timeout=10)
    resp.raise_for_status()
