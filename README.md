# 🔮 오늘의 MBTI 운세

내 MBTI를 고르면 **오늘의 운세**를 한 줄 운세 · 대인관계 · 일/학업 · 생활 리듬으로 알려주는 웹 서비스.

**👉 바로 보기: https://yeorm123.github.io/mbti-fortune/**

![서비스 화면](docs/images/screenshot.jpg)

## 주요 기능

- **16유형 선택** — 버튼 한 번으로 내 유형의 오늘 운세 확인
- **오늘의 운세 카드** — 한 줄 운세 + 대인관계 / 일·학업 / 생활 리듬 + 행운의 색·아이템
- **날짜 넘기기** — ◀ ▶ 로 어제·내일 운세 보기
- **같은 날 = 같은 결과** — 날짜와 유형으로 문구를 골라, 언제 열어도 그날의 운세는 동일
- **지난번 유형 기억** — 다음에 열면 지난번 고른 유형에 표시
- **링크 공유** — `…/mbti-fortune/#ENFP` 처럼 유형별 링크 복사

## 만든 과정

자체 서비스 기획 과제로, 아래 순서대로 진행했다.

| 단계 | 내용 | 결과물 |
|---|---|---|
| 1. 폴더 만들기 | 프로젝트 전용 폴더 생성 | `mbti-fortune/` |
| 2. 계획 세우기 | 목표, 대상, 기능, 화면, 데이터, 일정 정리 | [docs/PLAN.md](docs/PLAN.md) |
| 3. 폴더 구조 정하기 | 계획·데이터·수집 코드·서비스 분리 | 아래 [폴더 구조](#폴더-구조) |
| 4. 레퍼런스 수집 | Firecrawl로 MBTI 운세 기사 30개(480건) 수집·분석 | [docs/REFERENCE.md](docs/REFERENCE.md) |
| 5. 운세 문구 작성 | 16유형 × 4항목 × 4문구 직접 작성 | [app/fortunes.json](app/fortunes.json) |
| 6. 화면 구현 | HTML/CSS/JS, 서버 없이 동작 | [app/](app/) |
| 7. 배포 | GitHub CLI(`gh`)로 저장소 생성 → GitHub Pages | 위 링크 |

## 폴더 구조

```
mbti-fortune/
├── app/                  실제 서비스 (GitHub Pages로 배포되는 폴더)
│   ├── index.html
│   ├── style.css
│   ├── app.js            날짜+유형 해시로 문구 선택
│   └── fortunes.json     직접 작성한 운세 문구
├── docs/
│   ├── PLAN.md           서비스 계획서
│   ├── REFERENCE.md      레퍼런스 수집·분석 보고서
│   └── images/
├── scripts/
│   └── crawl.py          Firecrawl 수집 스크립트
├── data/                 수집 데이터 (GitHub 제외)
└── .env                  Firecrawl API 키 (GitHub 제외)
```

## 기술 스택

| 구분 | 사용 |
|---|---|
| 화면 | HTML, CSS, JavaScript (프레임워크 없음) |
| 데이터 수집 | Python, [Firecrawl](https://firecrawl.dev) API |
| 배포 | GitHub CLI, GitHub Pages (`gh-pages` 브랜치) |

## 직접 실행하기

```bash
# 화면 띄우기
cd app
python -m http.server 8000      # http://localhost:8000

# 레퍼런스 다시 수집하기 (.env 에 FIRECRAWL_API_KEY=fc-... 필요)
pip install requests
python scripts/crawl.py
```

## 배포하기

```bash
git add -A && git commit -m "수정 내용" && git push
git subtree push --prefix app origin gh-pages   # app/ 폴더만 사이트로 배포
```

## 운세 문구는 어떻게 골라질까?

`날짜 + 유형 + 항목` 문자열을 해시(FNV-1a)해서 문구 목록의 번호를 정한다.
그래서 같은 날 같은 유형은 언제 열어도 같은 운세가 나오고, 날짜가 바뀌면 조합이 달라진다.

```js
const key = `${dateKey(date)}:${type}`;          // 예: "2026-10-12:INFP"
pick(t.one_line, key + ":one");                   // 한 줄 운세
pick(t.relationship, key + ":rel");               // 대인관계
```

## 참고 및 안내

- 레퍼런스: 비건뉴스 「오늘의 MBTI 운세」 기사 (분석용으로만 사용, 원문 미포함)
- 운세는 재미로 보는 콘텐츠이며 과학적 근거가 없습니다.
- MBTI®는 The Myers-Briggs Company의 상표이며, 이 프로젝트는 해당 회사와 관련이 없습니다.
