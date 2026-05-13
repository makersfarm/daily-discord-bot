def build_public_data_prompt(data: dict) -> str:
    datasets = "\n".join(
        f"{i+1}. {d['title']} ({d['org']})\n   설명: {d['desc'][:200]}\n   키워드: {d['keywords'][:100]}"
        for i, d in enumerate(data["datasets"])
    )
    return f"""오늘의 공공데이터 아이디어를 만들어줘.

분야: {data['category']}
오늘 선택된 공공데이터 API (3개):
{datasets}

각 데이터셋마다 그 데이터를 활용한 아이디어를 1개씩, 총 3개를 아래 형식으로 출력해.
- 데이터 요약은 1줄(50자 이내), 아이디어 설명도 1줄, 기능은 핵심만 2개.
- 기존에 유사한 한국 서비스가 있으면 마지막 줄에 참고로 표기. 없으면 그 줄 생략.
- 추가 질문이나 부연 설명(웹 검색 권한, Sources 등) 없이 바로 형식대로만 출력.
- 아이디어 사이 구분선(---)을 꼭 넣어줘.

형식 (각 데이터셋마다 반복):

**📁 데이터셋명** (기관)
데이터 한 줄 요약

### 💡 아이디어명
누구를 위해 어떤 문제를 푸는지 한 줄 설명
1️⃣ 핵심 기능
2️⃣ 핵심 기능
📎 참고: [유사서비스명](URL)

---
"""


def build_aihub_prompt(data: dict) -> str:
    tags = ", ".join(data["tags"]) if data["tags"] else "없음"
    desc_line = f"설명: {data['desc']}\n" if data.get("desc") else ""
    return f"""오늘의 AI Hub 데이터셋 아이디어를 만들어줘.

데이터셋명: {data['title']}
분야: {data['field']}
데이터 유형: {data['type']}
태그: {tags}
{desc_line}구축년도: {data['year']}
링크: {data['url']}

이 데이터셋을 활용한 아이디어를 2개, 아래 형식으로 출력해.
- 아이디어 설명은 1줄, 기능은 핵심만 2개.
- 기존에 유사한 한국 서비스가 있으면 마지막 줄에 참고로 표기. 없으면 그 줄 생략.
- 추가 질문이나 부연 설명(웹 검색 권한, Sources 등) 없이 바로 형식대로만 출력.
- 아이디어 사이 구분선(---)을 꼭 넣어줘.

형식 (2개 반복):

### 💡 아이디어명
누구를 위해 어떤 문제를 푸는지 한 줄 설명
1️⃣ 핵심 기능
2️⃣ 핵심 기능
📎 참고: [유사서비스명](URL)

---
"""
