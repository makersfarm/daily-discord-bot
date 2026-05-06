# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

매일 KST 09:00에 공공데이터 아이디어 + AI Hub 아이디어를 Discord로 전송하는 봇.
스케줄러는 **Claude Code 루틴** (GitHub Actions 아님). Claude가 `python3 main.py`를 실행하고, `claude` CLI로 아이디어를 직접 생성.

## Architecture

```
main.py                          # 진입점: 수집 → 아이디어 생성(claude CLI) → Discord 전송
src/
  collectors/
    public_data.py               # 공공데이터포털 API 실시간 조회
    aihub.py                     # data/aihub_catalog_detail.json 읽기 + seen 추적
  generators/
    idea.py                      # 프롬프트 빌더 (Claude CLI가 실행)
  senders/
    discord.py                   # Discord Webhook Embed 전송
data/
  aihub_catalog_detail.json      # AI Hub 805개 데이터셋 캐시 (크롤링 완료)
  aihub_catalog.json             # AI Hub ID+title만 있는 원본 목록
  public_data_all.json           # 공공데이터 16개 카테고리 전체 캐시 (로컬에서 월 1회 갱신)
  public_data_categories.json    # 공공데이터 16개 대분류 + 하위분류 매핑 (참고용)
  seen_aihub.json                # 이미 소개한 AI Hub 데이터셋 ID 목록 (자동 생성)
scripts/
  fetch_all_public_data.py       # 공공데이터 16개 카테고리 전체 fetch → data/public_data_all.json
```

## Key Design Decisions

### 공공데이터포털
- **실행 환경 주의**: Claude Code 루틴은 Anthropic 원격 서버(해외 IP)에서 실행됨. data.go.kr API는 국내 IP만 허용 → 루틴에서 직접 호출 시 403. **반드시 로컬에서 캐시 생성 후 push해야 함.**
- **캐시 파일**: `data/public_data_all.json` — 16개 카테고리 전체 데이터셋 저장
- **API 엔드포인트**: `https://api.odcloud.kr/api/15077093/v1/open-data-list`
- **분야 순환**: `day_of_year % 16` — state 파일 없이 날짜 기반 자동 순환
- **데이터 선택**: 캐시에서 오늘 카테고리 로드 → `list_id` seen 추적 → 랜덤 3개 선택
- **응답 주의**: `totalCount`는 항상 17190 반환 (API 버그). 실제 필터링은 됨.
- 16개 분야: 공공행정, 과학기술, 교통물류, 국토관리, 사회복지, 산업고용, 식품건강, 재난안전, 재정금융, 통일외교안보, 환경기상, 교육, 농축수산, 문화관광, 법률, 보건의료

### 공공데이터 캐시 갱신 (월 1회 권장)
```bash
source .env && python3 scripts/fetch_all_public_data.py
git add data/public_data_all.json
git commit -m "data: refresh public data cache"
git push
```

### AI Hub
- **카탈로그 엔드포인트**: `https://api.aihub.or.kr/info/dataset.do` (인증 불필요)
- **카탈로그 갱신**: 위 엔드포인트에서 목록 → 각 상세 페이지 크롤링 → `aihub_catalog_detail.json`
- **seen 추적**: `data/seen_aihub.json` 에 이미 소개한 ID 저장. 전부 소개하면 초기화.
- 14개 분야: 영상이미지·멀티모달, 한국어, 헬스케어, 교통물류, 농축수산, 재난안전환경 등

### 아이디어 생성
- `generators/idea.py`는 프롬프트 빌더만 담당
- `main.py`가 `claude -p "..." --model claude-haiku-4-5-20251001` subprocess 호출, timeout=120초
- Claude Code 루틴 환경에서 실행되므로 별도 API 키 불필요

### 데이터 파일 용도
- `aihub_catalog_detail.json` — 런타임에 직접 읽는 캐시. 갱신 필요시 크롤링 스크립트 재실행.
- `public_data_all.json` — 공공데이터 16개 카테고리 캐시. `scripts/fetch_all_public_data.py`로 갱신.
- `public_data_categories.json` — 런타임 미사용, 분야 구조 참고용 문서.
- `seen_aihub.json` — 실행 시 자동 생성/갱신. 805개 전부 소진되면 자동 초기화.
- **seen 추적 한계**: 루틴은 매 실행마다 fresh clone이라 seen 변경이 다음 실행에 반영 안 됨. 각 카테고리에 수십~수백 개 데이터셋이 있어 실용상 문제 없음.

## Running Locally

크리덴셜은 `.env`에 저장되어 있음. **반드시 프로젝트 루트에서 실행** (`aihub.py`가 `data/` 상대경로 사용).

```bash
pip install -r requirements.txt
source .env && python3 main.py
```

`python` 명령은 없고 `python3` 사용. `claude` CLI 경로: `/Applications/cmux.app/Contents/Resources/bin/claude`

## 루틴 설정

**Trigger ID**: `trig_01QpQUfwedzSEMmxuhdzysrh`  
**스케줄**: `3 0 * * *` (UTC) = KST 09:03  
**모델**: `claude-haiku-4-5-20251001`  
**allowed_tools**: `Bash`, `Write`  
**소스 레포**: `https://github.com/makersfarm/daily-discord-bot-cowork` (main 브랜치)

루틴 에이전트가 매일 실행하는 단계:
1. `.env` 파일 작성 (크리덴셜 주입)
2. `pip install -q -r requirements.txt`
3. `python3 main.py`

루틴 수정은 `RemoteTrigger` 툴로 가능 (Claude Code가 자동으로 OAuth 토큰 주입).

## Required Environment Variables

- `PUBLIC_DATA_SERVICE_KEY` — data.go.kr API 키 (루틴이 `.env`로 주입, 로컬은 `.env` 파일 직접 사용)
- `DISCORD_WEBHOOK_URL` — Discord 채널 Webhook URL (동일)
- `python-dotenv`가 `.env`를 자동 로드 (`main.py` 상단 `load_dotenv()`)

## 현재 상태 (2026-05-06 기준)

- 파이프라인 전체 구현 완료 (수집 → 아이디어 생성 → Discord 전송)
- 공공데이터 IP 차단 문제 해결: 16개 카테고리 전체 캐시(`data/public_data_all.json`, 2996개) 로컬 fetch 완료
- 루틴에서 API 호출 없이 캐시 파일만 읽어 동작
- `python-dotenv`로 `.env` 자동 로드 (루틴이 쓴 `.env`를 Python이 읽을 수 있게)
- claude CLI 타임아웃 120초 (`main.py:18`)
- **아직 Discord 전송까지 완전히 성공한 루틴 실행 없음** — 재테스트 필요

## TODO / 미완성

- [ ] 루틴 재실행 후 Discord 전송 확인
- [ ] AI Hub 카탈로그 정기 갱신 스크립트 (`scripts/update_aihub_catalog.py`)
- [ ] 에러 핸들링 강화 (API 실패 시 재시도)
