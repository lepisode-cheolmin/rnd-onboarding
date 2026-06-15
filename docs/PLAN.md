# Plan

> 본 문서는 [instruction.md](ref/instruction.md)의 과제 지침을 기반으로 작성한 개발 계획서입니다.
> 개발 착수 전 작성이 필수 산출물이며, 진행하며 갱신합니다.
> 주요 의사결정 근거는 [DECISION.md](DECISION.md)에 별도 기록합니다.

## 0. 진행 현황 (Progress)

- [x] 계획 수립 (PLAN.md / DECISION.md)
- [x] **환경 구성 (6장)** — uv 설치/검증 완료 (API 키 입력만 사용자 작업으로 남음)
- [x] 공통 스키마 정의 (7.1)
- [x] OpenAI 버전 구현 (7.4) — 코드 완료, 실행은 키 필요
- [x] LangChain 버전 구현 (7.5) — 코드 완료, 실행은 키 필요
- [x] 비교/정리 (7.6)
- [x] 검증 통과 (8장) — 두 노트북 실제 실행 성공 (gpt-5.4-nano, effort low)
- [ ] 제출 (9장)

## 1. 개요

| 항목 | 내용 |
| --- | --- |
| 과제 유형 | 자유주제 프로젝트형 |
| 소요일 | 1일 |
| 언어 | Python |
| 파일 형식 | Jupyter Notebook (`.ipynb`) |
| 패키지 관리 | uv |
| 가상환경 | uv 기반 venv |
| IDE / Agent | Antigravity / Claude Code |

## 2. 미션

자유 주제로 **프롬프트 매니징 + 구조화된 출력(Structured Output)** 파이프라인 구현.

### 제약사항 (필수)
- [ ] **OpenAI 클라이언트** 버전과 **LangChain 클라이언트** 버전 **두 가지**로 각각 구현
- [ ] 두 버전 모두 **Structured Output** 활용
- [ ] 패키지 관리: **uv** / 가상환경: **uv venv**
- [ ] 결과물: `.ipynb` 노트북
- [ ] 에이전트를 활용하되, **직접 설명 가능한 수준으로 이해**할 것

## 3. 주제: 영화 정보 구조화 출력기

영화 제목을 입력하면 해당 영화 정보를 검색해 **구조화된 형태로 출력**한다.

### 출력 필드 (Pydantic 스키마)
| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `title` | str | 영화명 |
| `release_date` | str (YYYY-MM-DD) | 개봉일 |
| `production` | str | 배급사/제작사 |
| `director` | str | 감독명 |
| `cast` | list[str] | 주요 배우 |
| `synopsis` | str | 줄거리 |
| `rating` | float | 별점/평점 |

## 4. 데이터 소스: OpenAI 내장 web_search

- **OpenAI 내장 `web_search` 툴**로 영화 정보를 검색한다. **`OPENAI_API_KEY` 하나면** 되고 별도 검색 키는 불필요.
- OpenAI 버전: `responses.parse(tools=[web_search], text_format=Movie)` — 검색+구조화 단일 호출.
- LangChain 버전: `bind_tools([web_search])` 검색 → `with_structured_output(Movie)` 구조화 (2단계 체인).

> 소스 변경 이력: TMDB → web_search. 네이버 미사용 사유 포함 근거는 [DECISION.md](DECISION.md) D-2 / D-3 참고.

## 5. 산출물 (Deliverables)
- `notebooks/01_openai_version.ipynb` — OpenAI 클라이언트 버전
- `notebooks/02_langchain_version.ipynb` — LangChain 클라이언트 버전
- `schemas.py` — 공통 Pydantic 스키마(`Movie`)
- `prompts/` — 구조화/버전 관리되는 프롬프트 템플릿
- `pyproject.toml`, `uv.lock` — uv 의존성 정의
- `README.md` — 실행 방법 및 구현 설명
- 본 `PLAN.md`

## 6. 환경 구성 (Python 미설치 → uv부터 시작)

> 현재 PC: **Python 미설치**, **uv 0.11.19 설치됨**, git 설치됨.
> uv가 Python 인터프리터까지 설치·관리하므로 시스템 Python 설치는 불필요.
> 구성 매뉴얼/주의점은 [draft/ENVIRONMENT.md](draft/ENVIRONMENT.md) 참고.

- [x] **0. uv로 Python 설치** — `uv python install 3.12` → Python 3.12.13 설치 완료
- [x] **1. 프로젝트 초기화** — `uv init --python 3.12` → `pyproject.toml` 생성 완료
- [x] **2. 가상환경 생성** — `uv venv` → `.venv` 생성 완료
- [x] **3. 런타임 의존성 추가** — `uv add openai langchain langchain-openai pydantic python-dotenv httpx` → 설치 완료 (openai 2.41.1 / langchain 1.3.9 / pydantic 2.13.4)
- [x] **4. 개발 의존성 추가** — `uv add --dev jupyter ipykernel` → 설치 완료. import 검증 통과 ✅
- [x] **5. API 키 설정** — `.env`에 `OPENAI_API_KEY` 작성 완료 (TMDB 키 불필요)
- [x] **6. 주피터 실행** — `uv run jupyter lab` / nbconvert 실행으로 두 노트북 전 셀 정상 실행 확인 ✅

## 7. 구현 계획

- [x] **7.1 공통 — Pydantic 스키마 (`Movie`)**: [schemas.py](../schemas.py)에 7개 필드 정의. 두 버전 공유. 검증 완료.
- [x] **7.2 데이터 검색**: OpenAI 내장 `web_search` 툴 사용 (각 노트북에 구현). 별도 모듈/키 불필요.
- [x] **7.3 프롬프트 매니징**: [prompts/](../prompts/__init__.py)에 v1/v2 레지스트리 + `$title`/`$context` 템플릿. 렌더링 검증 완료.
- [x] **7.4 버전 A — OpenAI 클라이언트**: [notebooks/01_openai_version.ipynb](../notebooks/01_openai_version.ipynb) — `responses.parse(tools=[web_search], text_format=Movie)`. 구성 검증 완료, 실행은 키 필요 ⏳
- [x] **7.5 버전 B — LangChain 클라이언트**: [notebooks/02_langchain_version.ipynb](../notebooks/02_langchain_version.ipynb) — `bind_tools([web_search])` → `with_structured_output(Movie)`. 구성 검증 완료, 실행은 키 필요 ⏳
- [x] **7.6 비교 / 정리**: 각 노트북에 v1/v2 프롬프트 비교 + 정리 마크다운 셀 포함.

## 8. 검증 (Definition of Done)
- [x] `uv run` 환경에서 두 노트북이 처음부터 끝까지 에러 없이 실행 (nbconvert --execute, 에러 0건)
- [x] 두 버전 모두 Pydantic 스키마(`Movie`)로 구조화된 출력 반환 확인
- [x] 프롬프트 v1/v2 변형에 따른 출력 차이 시연 셀 포함·실행
- [x] 구현 내용 설명 문서화: [draft/NOTEBOOKS.md](draft/NOTEBOOKS.md) 등

> 사용 모델: `gpt-5.4-nano`, reasoning effort `low`. (검증 방법은 [draft/TESTING.md](draft/TESTING.md) 참고)

## 9. 제출
- 회사 **개인** 레퍼지토리에 업로드 (lepisode organization 아님)
- 파일 공유 및 구현 내용 발표

## 10. 리스크 / 메모
- OpenAI API 키만 필요(비용 확인). 웹검색도 OpenAI 키로 동작 → TMDB 키 불필요.
- 웹검색 결과는 정형 API보다 재현성↓·환각 가능성 → 프롬프트 v2에서 "사실만 근거, 추측 금지"로 완화.
- `.env`는 반드시 `.gitignore` 처리 (키 유출 방지).
- OpenAI/LangChain 버전에 따라 structured output API 시그니처 상이 → 설치 후 버전 확인.
- 의사결정 로그: [DECISION.md](DECISION.md)
