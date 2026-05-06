import json
import os
import subprocess
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from src.collectors import public_data, aihub
from src.generators.idea import build_public_data_prompt, build_aihub_prompt
from src.senders import discord

PAYLOAD_PATH = Path("data/today_discord_payload.json")


def ask_claude(prompt: str) -> str:
    env = {**os.environ, "CLAUDECODE": ""}
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", "claude-haiku-4-5-20251001"],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI 오류: {result.stderr}")
    return result.stdout.strip()


def main():
    day_of_year = date.today().timetuple().tm_yday

    print("📊 공공데이터포털 수집 중...")
    pub_data = public_data.collect(day_of_year)
    print(f"  분야: {pub_data['category']}, {len(pub_data['datasets'])}개 선택")

    print("🤖 AI Hub 수집 중...")
    hub_data = aihub.collect()
    print(f"  데이터셋: {hub_data['title']}")

    print("💡 아이디어 생성 중...")
    pub_idea = ask_claude(build_public_data_prompt(pub_data))
    hub_idea = ask_claude(build_aihub_prompt(hub_data))

    payload = discord.build_payload(pub_data, hub_data, pub_idea, hub_idea)
    PAYLOAD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 payload 저장: {PAYLOAD_PATH}")

    try:
        discord.send(pub_data, hub_data, pub_idea, hub_idea)
        print("📨 Discord 직접 전송 성공")
    except Exception as e:
        print(f"⚠️ Discord 직접 전송 실패 (GitHub Actions가 처리): {e}")

    print("\n--- 공공데이터 아이디어 ---")
    print(pub_idea)
    print("\n--- AI Hub 아이디어 ---")
    print(hub_idea)


if __name__ == "__main__":
    main()
