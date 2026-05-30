"""금연두드림(nosmokeguide.go.kr) '금연방법' 정보자료 스크래퍼.

RAG 인덱싱용 생활습관(금연) 자료 수집. CKD 지식 베이스에 비어 있던 금연 축을 채운다.
본문은 목록 API에 미리보기만 오므로, 상세 API의 contentList[].htmlFileUrl 에서 전체를 받는다.

라이선스: 공공누리(출처표시 + 상업적 이용금지 + 변경금지). 비상업 교육 프로젝트라 사용 가능하며,
각 .md frontmatter 에 출처(source_url)·작성자·라이선스를 기록해 출처표시 의무를 지킨다.

재실행하면 최신 목록으로 갱신된다. 표준 라이브러리만 사용(외부 의존성 없음).
"""
import html
import json
import re
import time
import urllib.request
from pathlib import Path

BASE = "https://www.nosmokeguide.go.kr"
LIST_API = (
    BASE + "/api/integrate/info-data/quit-smoking-methods"
    "?pageNum=1&pageSize=100&categoryCode=all&searchColumn=all&searchKeyword="
)
DETAIL_API = BASE + "/api/integrate/info-data/quit-smoking-methods/{}?categoryCode=all"
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "lifestyle" / "nosmokeguide"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def fetch(url: str) -> str:
    """UA 헤더를 붙여 텍스트를 받는다 (정부 사이트는 UA 없으면 차단)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def html_to_text(raw: str) -> str:
    """블록 태그를 줄바꿈으로 바꾼 뒤 태그를 제거해 본문 텍스트만 남긴다."""
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", raw)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?i)</(p|div|h[1-6]|li|tr|table|section|article)>", "\n", raw)
    raw = re.sub(r"<[^>]+>", "", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def extract_items(payload: dict) -> list:
    """목록 API 응답에서 항목 리스트를 찾는다 (data 가 list 또는 중첩 dict)."""
    data = payload["data"]
    if isinstance(data, list):
        return data
    for value in data.values():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value
    raise ValueError("목록 항목을 찾지 못했습니다")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = extract_items(json.loads(fetch(LIST_API)))
    print(f"목록 {len(items)}건 수신")

    saved = 0
    for item in items:
        data_id = item["dataId"]
        detail = json.loads(fetch(DETAIL_API.format(data_id)))["data"]
        title = (detail.get("title") or "").strip()
        category = detail.get("dataType") or ""
        info = detail.get("detailInfo") or {}
        license_type = detail.get("licenseType") or ""

        keywords: list[str] = []
        bodies: list[str] = []
        for content in detail.get("contentList") or []:
            keywords += content.get("keywordList") or []
            file_url = content.get("htmlFileUrl")
            if file_url:
                bodies.append(html_to_text(fetch(file_url)))
            time.sleep(0.2)

        body = "\n\n".join(b for b in bodies if b).strip()
        if not body:
            print(f"  - {data_id} 본문 없음, 건너뜀")
            continue

        keywords = list(dict.fromkeys(keywords))  # 중복 제거, 순서 유지
        frontmatter = [
            "---",
            f"dataId: {data_id}",
            f"title: {title}",
            f"category: {category}",
            "source: nosmokeguide.go.kr",
            f"source_url: {BASE}/information/method/{data_id}",
            f"writer: {info.get('writer', '')}",
            f"writeDate: {info.get('writeDate', '')}",
            f"license: {license_type}",
            f"keywords: {', '.join(keywords)}",
            "---",
            "",
            f"# {title}",
            "",
            body,
            "",
        ]
        (OUT_DIR / f"nsg_{data_id}.md").write_text("\n".join(frontmatter), encoding="utf-8")
        saved += 1
        print(f"  ✓ {data_id} {title[:30]} ({len(body)}자)")
        time.sleep(0.3)

    print(f"\n완료: {saved}/{len(items)}건 저장 → {OUT_DIR}")


if __name__ == "__main__":
    main()
