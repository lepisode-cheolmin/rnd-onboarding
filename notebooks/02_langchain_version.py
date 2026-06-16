# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 영화 정보 구조화 — LangChain 클라이언트 버전
#
# 영화 제목 입력 → **web_search 툴로 검색**(`bind_tools`) → **Structured Output**(`with_structured_output`)으로 공통 `Movie` 스키마에 맞춰 구조화한다.
#
# OpenAI 버전과 **동일한 스키마/프롬프트**를 공유한다. 다른 점은 흐름을 **2단계 체인**으로 나눈 것.

# %% [markdown]
# ## 1. 환경 설정

# %%
from pathlib import Path
from dotenv import load_dotenv

# .env 로드를 위해 프로젝트 루트 찾기 (pyproject.toml 기준).
# rnd_onboarding 패키지는 설치돼 있어 import 경로 조작은 불필요하다.
ROOT = Path.cwd()
if not (ROOT / "pyproject.toml").exists():
    ROOT = ROOT.parent
load_dotenv(ROOT / ".env")

TITLE = "인터스텔라"  # ← 원하는 영화 제목으로 변경
MODEL = "gpt-5.4-nano"  # web_search + structured output 지원
EFFORT = "low"          # reasoning effort (low: 빠르고 저렴)
print("ROOT:", ROOT, "| TITLE:", TITLE, "| MODEL:", MODEL, "| effort:", EFFORT)

# %% [markdown]
# ## 2. 1단계 — web_search 툴로 검색
#
# 내장 툴 `{"type": "web_search"}` 를 bind 하면 LangChain 이 자동으로 Responses API 로 전환해 서버측에서 검색을 수행한다. 결과 텍스트(findings)를 얻는다.

# %%
from langchain_openai import ChatOpenAI
from rnd_onboarding import prompts
from rnd_onboarding.schemas import Movie


def as_text(msg):
    """AIMessage.content(문자열 또는 블록 리스트)를 평범한 텍스트로 변환."""
    content = msg.content
    if isinstance(content, str):
        return content
    parts = [block.get("text", "") if isinstance(block, dict) else str(block) for block in content]
    return "\n".join(part for part in parts if part)


search_llm = ChatOpenAI(
    model=MODEL, use_responses_api=True, reasoning_effort=EFFORT
).bind_tools([{"type": "web_search"}])
search_msg = search_llm.invoke(
    f"영화 '{TITLE}' 의 개봉일, 배급사/제작사, 감독, 주요 출연진, 줄거리, 평점을 웹에서 찾아 정리해줘."
)
findings = as_text(search_msg)
print(findings)

# %% [markdown]
# ## 3. 2단계 — 구조화
#
# 검색 결과(findings)를 `with_structured_output(Movie)` 로 스키마에 맞춰 구조화한다.

# %%
struct_llm = ChatOpenAI(model=MODEL, reasoning_effort=EFFORT).with_structured_output(Movie)

msgs = prompts.render("v2", TITLE, findings=findings)
movie = struct_llm.invoke([
    ("system", msgs["system"]),
    ("human", msgs["user"]),
])
print(movie.pretty())

# %%

# %% [markdown]
# ## 4. 프롬프트 매니징 — v1 vs v2 비교
#
# 검색은 한 번만 하고(findings 재사용), 구조화 프롬프트만 v1/v2 로 바꿔 비교한다.

# %%
for v in prompts.list_versions():
    msgs = prompts.render(v, TITLE, findings=findings)
    m = struct_llm.invoke([
        ("system", msgs["system"]),
        ("human", msgs["user"]),
    ])
    print(f"=== prompt {v} ===")
    print(m.model_dump_json(indent=2))
    print()

# %% [markdown]
# ## 5. 정리
#
# - LangChain 은 **검색(`bind_tools`) → 구조화(`with_structured_output`)** 를 2단계 체인으로 구성.
# - OpenAI 버전과 동일 스키마 → 결과 구조가 같다. 차이는 흐름의 추상화 방식.
# - 2단계로 나누면 검색 결과를 재사용하거나 중간에 가공하기 쉽다(프롬프트 비교처럼).
