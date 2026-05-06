# Daily Idea Bot

매일 KST 13:00에 공공데이터 + AI Hub 데이터셋 기반 아이디어를 Discord로 전송하는 봇.

## 구조

```
Claude Code 루틴 (Anthropic 서버)
  └─ python3 main.py
       ├─ 공공데이터포털: data/public_data_all.json (16개 카테고리 캐시)
       ├─ AI Hub: data/aihub_catalog_detail.json (805개 데이터셋 캐시)
       ├─ Claude Haiku로 아이디어 생성
       └─ GitHub API → workflow_dispatch 트리거

GitHub Actions (discord_send.yml)
  └─ Discord Webhook으로 임베드 메시지 전송
```

**Discord에서 discord.com을 차단하는 Anthropic 서버 특성상**, 루틴이 직접 Discord를 호출하지 않고 GitHub Actions를 릴레이로 사용합니다.

## 로컬 실행

```bash
pip install -r requirements.txt
source .env && python3 main.py
```

`.env`:
```
PUBLIC_DATA_SERVICE_KEY=...
DISCORD_WEBHOOK_URL=...
GITHUB_TOKEN=...   # 로컬에서 GH Actions 폴백 시 필요 (직접 전송 성공 시 불필요)
```

## 공공데이터 캐시 갱신 (월 1회 권장)

data.go.kr API는 국내 IP만 허용. 로컬에서 실행 후 push.

```bash
source .env && python3 scripts/fetch_all_public_data.py
git add data/public_data_all.json
git commit -m "data: refresh public data cache"
git push
```

## 파일 구조

```
main.py                              진입점
src/collectors/public_data.py        공공데이터 수집 (캐시 기반)
src/collectors/aihub.py              AI Hub 수집 (캐시 기반)
src/generators/idea.py               Claude 프롬프트 빌더
src/senders/discord.py               Discord 전송 / payload 빌드
data/public_data_all.json            공공데이터 16개 카테고리 캐시
data/aihub_catalog_detail.json       AI Hub 805개 데이터셋 캐시
data/today_discord_payload.json      오늘 생성된 Discord payload
scripts/fetch_all_public_data.py     공공데이터 캐시 갱신 스크립트
.github/workflows/discord_send.yml  Discord 전송 GitHub Actions
```
