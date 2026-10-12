"""비건뉴스 '오늘의 MBTI 운세' 기사를 Firecrawl로 수집해 JSON/CSV로 저장한다.

실행: python scripts/crawl.py            (태그 목록 전체 페이지)
      python scripts/crawl.py --pages 1  (최근 1페이지만)
"""

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"

API_URL = "https://api.firecrawl.dev/v2/scrape"
TAG_URL = "https://www.vegannews.co.kr/news/tag_list_all.html?tag=MBTI%20%EC%9A%B4%EC%84%B8&page={page}"
ARTICLE_RE = re.compile(r"https://www\.vegannews\.co\.kr/news/article\.html\?no=(\d+)")
TYPE_RE = re.compile(r"^\s*([IE][NS][TF][JP])(?:\s*운세)?\s*$", re.M)
GROUP_RE = re.compile(r"^\s*[가-힣]{2,6}형\s*$", re.M)
FIELD_RE = re.compile(r"(?:^|\n)\s*-?\s*([가-힣·\s]{2,10}?)\s*:\s*")

FIELD_NAMES = {
    "한 줄 운세": "one_line",
    "대인관계": "relationship",
    "일·학업": "work_study",
    "생활 리듬": "daily_rhythm",
}


def load_api_key():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("FIRECRAWL_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"FIRECRAWL_API_KEY가 {ENV_PATH}에 없습니다.")


def scrape(api_key, url, retries=3):
    for attempt in range(retries):
        res = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
            timeout=120,
        )
        if res.status_code == 429:
            time.sleep(10 * (attempt + 1))
            continue
        res.raise_for_status()
        body = res.json()
        if body.get("success"):
            return body["data"]["markdown"]
        time.sleep(3)
    raise RuntimeError(f"scrape 실패: {url}")


def collect_article_ids(api_key, max_pages):
    ids = []
    for page in range(1, max_pages + 1):
        md = scrape(api_key, TAG_URL.format(page=page))
        # 목록 영역만 사용 (사이드바 '많이 본 기사' 링크 제외)
        listing = md.split("tag_list_all.html?tag=MBTI%20%EC%9A%B4%EC%84%B8&page=0")[0]
        found = [n for n in ARTICLE_RE.findall(listing) if n not in ids]
        print(f"목록 {page}페이지: 기사 {len(found)}개")
        if not found:
            break
        ids.extend(found)
    return ids


def parse_article(no, md):
    title = re.search(r"^# (.+)$", md, re.M)
    date = re.search(r"등록 (\d{4})\.(\d{2})\.(\d{2})", md)
    body = md.split("※ 이 기사는")[0].split("Copyright")[0]
    body = body.replace("\\-", "\n-").replace("\\\\", "")

    matches = list(TYPE_RE.finditer(body))
    intro = ""
    if matches:
        head = body[: matches[0].start()]
        paras = [p.strip() for p in head.split("\n\n") if "MBTI 운세" in p and not p.startswith(("#", "[", "!"))]
        intro = paras[-1] if paras else ""

    rows = []
    for i, m in enumerate(matches):
        seg = body[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(body)]
        seg = GROUP_RE.sub("", seg)
        keys = list(FIELD_RE.finditer(seg))
        fields = {}
        if not keys:  # 7~8월 기사: 항목 구분 없는 문단형
            fields["text"] = " ".join(seg.split())
        for j, k in enumerate(keys):
            end = keys[j + 1].start() if j + 1 < len(keys) else len(seg)
            fields[k.group(1).strip()] = " ".join(seg[k.end():end].split()).strip(" -")
        rows.append({"mbti": m.group(1), **{FIELD_NAMES.get(k, k): v for k, v in fields.items()}})

    return {
        "article_no": int(no),
        "url": f"https://www.vegannews.co.kr/news/article.html?no={no}",
        "title": title.group(1).strip() if title else "",
        "date": "-".join(date.groups()) if date else "",
        "intro": intro,
        "fortunes": rows,
        "ai_generated_note": "생성형 AI를 활용해 구성" in md,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=20)
    args = ap.parse_args()

    api_key = load_api_key()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    ids = collect_article_ids(api_key, args.pages)
    print(f"총 기사 {len(ids)}개")

    articles = []
    for no in ids:
        raw_path = RAW_DIR / f"{no}.md"
        if raw_path.exists():
            md = raw_path.read_text(encoding="utf-8")
        else:
            md = scrape(api_key, f"https://www.vegannews.co.kr/news/article.html?no={no}")
            raw_path.write_text(md, encoding="utf-8")
        art = parse_article(no, md)
        print(f"  {art['date']} {art['title']} → {len(art['fortunes'])}개 유형")
        articles.append(art)

    articles.sort(key=lambda a: a["date"])
    (DATA_DIR / "mbti_fortune.json").write_text(
        json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    cols = ["date", "mbti", "one_line", "relationship", "work_study", "daily_rhythm", "text", "title", "url"]
    with open(DATA_DIR / "mbti_fortune.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for a in articles:
            for r in a["fortunes"]:
                w.writerow({**r, "date": a["date"], "title": a["title"], "url": a["url"]})

    print(f"저장 완료: {DATA_DIR / 'mbti_fortune.json'}, {DATA_DIR / 'mbti_fortune.csv'}")


if __name__ == "__main__":
    main()
