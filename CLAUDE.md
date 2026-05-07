# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

매일 KST 13:00에 공공데이터포털 + AI Hub 데이터셋 기반 아이디어를 Discord로 전송하는 봇. 스케줄러는 **Claude Code 루틴** (`trig_01QpQUfwedzSEMmxuhdzysrh`). `python3 main.py`를 실행하고 `claude` CLI로 아이디어를 직접 생성.

## 로컬 실행

반드시 프로젝트 루트에서 실행 (`aihub.py`가 `data/` 상대경로 사용).

```bash
pip install -r requirements.txt
source .env && python3 main.py
```

`python` 명령 없음, `python3` 사용. `claude` CLI 경로: `/Applications/cmux.app/Contents/Resources/bin/claude`

## 핵심 아키텍처

```
main.py
  └─ public_data.collect()      data/public_data_all.json 읽기 (day_of_year % 16으로 카테고리 선택)
  └─ aihub.collect()            data/aihub_catalog_detail.json 읽기 (seen 추적)
  └─ ask_claude() ×2            claude -p "..." --model claude-haiku-4-5-20251001, timeout=120s
  └─ discord.build_payload()    Discord embeds 구조 빌드
  └─ discord.send()             로컬에선 성공, 루틴 환경에선 discord.com 차단으로 실패
  └─ _trigger_github_actions()  send() 실패 시 폴백: GitHub API workflow_dispatch 호출
                                  → .github/workflows/discord_send.yml → Discord Webhook
                                  (push 트리거도 있음: today_discord_payload.json 변경 감지)
```

### 환경별 Discord 전송 경로

| 환경 | 경로 |
|------|------|
| 로컬 | `discord.send()` 직접 호출 (성공) |
| 루틴 | `discord.send()` 실패 → `_trigger_github_actions()` → GitHub Actions → Discord |

루틴 환경(Anthropic 원격 서버)에서 `discord.com`과 `data.go.kr` 모두 IP 차단됨.

### 공공데이터 캐시

data.go.kr API는 국내 IP 전용. 루틴에서 직접 호출 불가 → **로컬에서 월 1회 갱신 후 push**.

```bash
source .env && python3 scripts/fetch_all_public_data.py
git add data/public_data_all.json && git commit -m "data: refresh public data cache" && git push
```

`totalCount`는 항상 17190 반환하는 API 버그 있음 (실제 필터링은 정상).

### AI Hub seen 추적

`data/seen_aihub.json`에 소개한 데이터셋 ID 저장. 루틴은 매 실행마다 fresh clone이라 seen 변경이 다음 실행에 반영 안 됨 — 805개 데이터셋이라 실용상 문제 없음.

## 루틴 설정

**Trigger ID**: `trig_01QpQUfwedzSEMmxuhdzysrh`  
**스케줄**: `0 4 * * *` (UTC) = KST 13:00  
**모델**: `claude-haiku-4-5-20251001` / **allowed_tools**: `Bash`, `Write`  
**소스 레포**: `https://github.com/makersfarm/daily-discord-bot-cowork` (main 브랜치)

루틴 프롬프트가 `.env`에 크리덴셜 직접 주입 (PUBLIC_DATA_SERVICE_KEY, DISCORD_WEBHOOK_URL, GITHUB_TOKEN). `python-dotenv`가 자동 로드.

루틴 수정: `RemoteTrigger` 툴 (Claude Code가 OAuth 토큰 자동 주입).

## 환경변수

- `PUBLIC_DATA_SERVICE_KEY` — data.go.kr API 키
- `DISCORD_WEBHOOK_URL` — Discord Webhook URL (로컬 `.env` + GitHub repo secret 둘 다 필요)
- `GITHUB_TOKEN` — GitHub OAuth token, `_trigger_github_actions()` 폴백용

GitHub repo secret: `Settings → Secrets and variables → Actions → DISCORD_WEBHOOK_URL`

## TODO

- [ ] AI Hub 카탈로그 정기 갱신 스크립트 (`scripts/update_aihub_catalog.py`)
