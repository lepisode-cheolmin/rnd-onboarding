# 영화 정보 구조화 출력기 (Structured Output 실습)

영화 제목을 입력하면 **OpenAI 내장 web_search 툴로 웹을 검색**하고, LLM의 **Structured Output**으로
공통 `Movie` 스키마에 맞춰 구조화해 출력한다.
**OpenAI 클라이언트**와 **LangChain 클라이언트** 두 가지 버전으로 구현한다.

> 과제 지침: [docs/ref/instruction.md](docs/ref/instruction.md) · 계획: [docs/PLAN.md](docs/PLAN.md) · 의사결정: [docs/DECISION.md](docs/DECISION.md)

## 구조

```
.
├── schemas.py                      # 공통 Pydantic 스키마 (Movie)
├── prompts/__init__.py             # 버전별 프롬프트 레지스트리 (v1, v2)
├── notebooks/
│   ├── 01_openai_version.ipynb     # OpenAI 버전 (검색+구조화 단일 호출)
│   └── 02_langchain_version.ipynb  # LangChain 버전 (검색 → 구조화 2단계 체인)
├── scripts/build_notebooks.py      # 노트북 재생성 스크립트
└── docs/                           # 계획/의사결정/학습 문서
```

## 빠른 시작

```powershell
# 1) 의존성 복원 (Python 3.12 + 패키지 일괄)
uv sync

# 2) API 키 설정 (OpenAI 키 하나면 됨 — 검색도 OpenAI 키로 동작)
Copy-Item .env.example .env
#   .env 에 OPENAI_API_KEY 입력

# 3) 주피터 실행
uv run jupyter lab
#   notebooks/01_openai_version.ipynb 또는 02_langchain_version.ipynb 열고 실행
```

자세한 환경 구성/주의점은 [docs/draft/ENVIRONMENT.md](docs/draft/ENVIRONMENT.md) 참고.

## 핵심 설계

- **공통 스키마**: 두 버전이 동일한 `Movie`(영화명·개봉일·제작사·감독·출연·줄거리·평점)를 공유 → 결과 비교가 쉽다.
- **데이터 소스 = OpenAI 내장 web_search**: `OPENAI_API_KEY` 하나로 검색까지 처리, 별도 검색 키 불필요. 네이버는 robots.txt로 봇/AI 접근을 차단하므로 사용하지 않는다([DECISION.md](docs/DECISION.md) D-2/D-3).
- **프롬프트 매니징**: `prompts` 모듈이 버전(v1, v2)을 관리하고 `$title`/`$context`(검색 결과) 변수를 주입한다.
- **Structured Output**:
  - OpenAI → `client.responses.parse(tools=[{"type":"web_search"}], text_format=Movie)` — 검색+구조화 단일 호출
  - LangChain → `bind_tools([{"type":"web_search"}])` 검색 → `with_structured_output(Movie)` 구조화

## 키 없이 검증된 부분 / 키 필요 부분

- ✅ 모듈 import, 스키마 인스턴스화, 프롬프트 렌더링, 두 클라이언트의 web_search + structured output **구성**(SDK 시그니처)까지 검증 완료.
- ⏳ 실제 웹검색 + LLM 호출은 `.env`에 `OPENAI_API_KEY` 입력 후 노트북에서 실행 필요.
