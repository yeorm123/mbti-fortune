# MBTI 오늘의 운세

내 MBTI를 고르면 오늘의 운세(대인관계·일/학업·생활 리듬)를 보여주는 웹 서비스.
자세한 계획은 [docs/PLAN.md](docs/PLAN.md) 참고.

## 레퍼런스 데이터 수집

```bash
# .env 에 FIRECRAWL_API_KEY=fc-... 저장 후
python scripts/crawl.py            # 태그 목록 전체
python scripts/crawl.py --pages 1  # 최근 1페이지만
```

결과: `data/mbti_fortune.json`, `data/mbti_fortune.csv` (원문은 `data/raw/`, 모두 GitHub 제외)
