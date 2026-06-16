# DECISION LOG

프로젝트 진행 중 내린 주요 의사결정과 그 근거를 기록합니다. ([PLAN.md](PLAN.md) 참고)

---

## D-1. 자유 주제 선정

- **결정:** "영화 정보 구조화 출력기" — 영화 제목 입력 → 영화 정보를 검색해 구조화된 형태로 출력.
- **출력 필드:** 영화명, 개봉일, 배급사/제작사, 감독, 출연진, 시놉시스, 평점.
- **근거:** Structured Output(Pydantic 스키마)의 효과를 명확히 보여주기 좋고, 1일 분량으로 적절.
- **일자:** 2026-06-15

---

## D-2. 데이터 소스 — 네이버 불가, TMDB 채택

- **결정:** 데이터 소스로 **TMDB API**(The Movie Database)를 사용한다. **네이버는 사용하지 않는다.**

### 근거 1 — 네이버는 봇/AI 접근을 명시적으로 차단 (robots.txt 확인, 2026-06-15)
- `movie.naver.com/robots.txt`
  ```
  User-agent: *
  Disallow: /
  ```
  (네이버 영화 서비스는 2021년 종료되어 검색으로 통합됨)
- `search.naver.com/robots.txt`
  ```
  User-agent: *
  Disallow: /

  # BOT ACCESS FOR THE PURPOSES OF AI TRAINING AND RETRIEVAL-AUGMENTED GENERATION (RAG) IS STRICTLY PROHIBITED.
  User-agent: GPTBot
  Disallow: /
  User-agent: OAI-SearchBot
  Disallow: /
  User-agent: ClaudeBot
  Disallow: /
  User-agent: Claude-SearchBot
  Disallow: /
  ... (PerplexityBot, Google-Extended, CCBot 등 동일)
  ```
- `www.naver.com/robots.txt` → 홈(`/$`) 외 전부 `Disallow`.

**보충 — 서브도메인 전수 확인 (2026-06-16):** `blog`/`news`/`cafe` 까지 모두 AI 봇을 차단했다.

| 도메인 | 일반 크롤러(`*`) | AI 봇(OAI-SearchBot/GPTBot 등) | web_search 사용 |
| --- | --- | --- | --- |
| `news.naver.com` | `Disallow: /` 전면 차단 (페북/트위터 미리보기만 허용) | 명시 차단 | ❌ |
| `cafe.naver.com` | `Disallow: /` 전면 차단 | 명시 차단 | ❌ |
| `blog.naver.com` | 일부 동적 endpoint만 차단, **게시글 본문은 허용** | 명시 차단 | ❌ |
| `m.blog.naver.com` | 본문 허용(특정 endpoint 차단) | 명시 차단 | ❌ |

- 모든 서브도메인 robots.txt 상단에 동일한 `# ... AI TRAINING AND RAG IS STRICTLY PROHIBITED` 블록 + `OAI-SearchBot/GPTBot/ClaudeBot/PerplexityBot/Google-Extended/CCBot ... Disallow: /`.
- 핵심: `blog.naver` 처럼 **일반 검색엔진엔 본문을 열어주는 곳도 AI 봇만 콕 집어 차단**한다 = "사람용 검색은 허용, AI 검색/RAG는 거부"가 네이버의 일관된 정책.
- **결론:** 네이버 스크래핑/검색은 robots.txt 위반이며 AI 용도는 명시적으로 금지됨. **`blog`/`news` 포함 네이버 전 도메인을 web_search 소스에서 제외**한다 → 과제 소스로 부적합.

### 근거 2 — TMDB가 요구 필드를 전부 충족
- 공식 무료 API, 한국어(`language=ko-KR`) 지원.
- 필드 매핑: 영화명·개봉일(`release_date`)·제작사(`production_companies`)·감독/출연(`credits`)·시놉시스(`overview`)·평점(`vote_average`) 전부 제공.

### 검토했으나 채택하지 않은 대안
- **KOBIS 오픈API:** 한국영화 공식 데이터지만 별점·시놉시스 미제공 → 필드 부족.
- **LLM 내장 웹검색:** 가능하나 결과 재현성/필드 일관성이 API보다 낮음.

- **일자:** 2026-06-15
- **상태:** ⚠️ **D-3에 의해 대체됨 (superseded).** 네이버 미사용 근거(근거 1)는 여전히 유효하나, 데이터 소스는 TMDB → OpenAI 내장 웹검색으로 변경.

---

## D-3. 데이터 소스 변경 — TMDB → OpenAI 내장 web_search (D-2 대체)

- **결정:** TMDB API 대신 **OpenAI 내장 `web_search` 툴**로 영화 정보를 검색한다.
- **근거:**
  - TMDB는 별도 가입/API 키 발급이 필요해 번거롭다(사용자 요청).
  - OpenAI `web_search` 툴은 **`OPENAI_API_KEY` 하나로** 동작 → 추가 검색 키(TMDB/Tavily 등) 불필요.
  - 네이버 직접 접근이 아니라 OpenAI가 robots 준수 검색엔진을 통해 검색하므로 D-2의 네이버 차단 이슈와 무관.
- **구현 방식 (검증된 SDK 시그니처 기반):**
  - **OpenAI 버전:** `client.responses.parse(tools=[{"type":"web_search"}], text_format=Movie)` — 검색+구조화 **단일 호출**. (설치된 openai 2.41.1 의 `responses.parse` 가 `tools`+`text_format` 동시 지원 확인)
  - **LangChain 버전:** `ChatOpenAI(...).bind_tools([{"type":"web_search"}])` 로 검색(자동 Responses API 전환) → `with_structured_output(Movie)` 로 구조화. **2단계 체인.**
- **트레이드오프(인지하고 수용):** 웹검색 결과는 TMDB 정형 데이터보다 재현성이 낮고 환각 가능성이 있다. → 프롬프트(v2)에서 "웹에서 찾은 사실만 근거, 추측 금지"로 완화.
- **후속 작업:** `.env`에 `OPENAI_API_KEY`만 설정. (TMDB 키 불필요)
- **일자:** 2026-06-15
