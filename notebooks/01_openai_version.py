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
#     display_name: rnd-onboarding (3.12.13)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 영화 정보 구조화 — OpenAI 클라이언트 버전
#
# 영화 제목 입력 → **OpenAI 내장 web_search 툴로 검색** → **Structured Output**으로 공통 `Movie` 스키마에 맞춰 구조화한다.
#
# `responses.parse(tools=[web_search], text_format=Movie)` 한 번의 호출로 **검색과 구조화가 동시에** 일어난다.
#
# > 사전 준비: `.env` 에 `OPENAI_API_KEY` 만 있으면 된다 (검색 키 불필요). 실행: `uv run jupyter lab`.

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
# ## 2. 검색 + 구조화 (단일 호출)
#
# `tools=[{"type": "web_search"}]` 로 모델이 직접 웹을 검색하고, `text_format=Movie` 로 결과를 `Movie` 스키마에 맞춰 돌려준다.

# %%
from openai import OpenAI
from rnd_onboarding import prompts
from rnd_onboarding.schemas import Movie

client = OpenAI()

msgs = prompts.render("v2", TITLE)  # findings 없음 → 모델이 web_search 로 직접 검색
resp = client.responses.parse(
    model=MODEL,
    tools=[{"type": "web_search"}],
    reasoning={"effort": EFFORT},
    input=[
        {"role": "system", "content": msgs["system"]},
        {"role": "user", "content": msgs["user"]},
    ],
    text_format=Movie,
)
movie = resp.output_parsed
print(movie.pretty())

# %% [markdown]
# ## 3. 프롬프트 매니징 — v1 vs v2 비교
#
# 같은 영화에 프롬프트 버전만 바꿔 끼우며 출력 차이를 비교한다 (`prompts` 모듈이 버전 관리).

# %%
for v in prompts.list_versions():
    msgs = prompts.render(v, TITLE)
    resp = client.responses.parse(
        model=MODEL,
        tools=[{"type": "web_search"}],
        reasoning={"effort": EFFORT},
        input=[
            {"role": "system", "content": msgs["system"]},
            {"role": "user", "content": msgs["user"]},
        ],
        text_format=Movie,
    )
    print(f"=== prompt {v} ===")
    print(resp.output_parsed.model_dump_json(indent=2))
    print()

# %% [markdown]
# ## 4. 정리
#
# - OpenAI Responses API 는 **툴 사용(web_search) + 구조화 출력(text_format)** 을 한 호출에 융합한다.
# - 반환 `resp.output_parsed` 가 곧 `Movie` 인스턴스 → 후처리 불필요.
# - LangChain 버전(`02_langchain_version.ipynb`)은 같은 일을 2단계 체인으로 한다 — 비교해 볼 것.
