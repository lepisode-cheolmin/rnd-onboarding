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
# # 한국 박스오피스 순위 — 구조화 출력
#
# 비정형 웹 검색 결과를 **순위 리스트 + 출처 URL**(`BoxOffice` 스키마)로 구조화한다.
# OpenAI / LangChain 두 버전 모두 web_search 로 검색한다.
#
# > ⚠️ 이 프로젝트의 목표는 **정확도가 아니라 "비정형 → structured output"**.
# > 네이버는 robots.txt 로 AI 봇을 차단하므로 사용하지 않고, KOBIS 기반 2차 출처에서 가져온다
# > (출처는 `sources` 에 그대로 노출해 투명하게 둔다). 자세한 근거는 `docs/DECISION.md` 참고.

# %% [markdown]
# ## 1. 환경 설정

# %%
from pathlib import Path
from dotenv import load_dotenv

# .env 로드를 위해 루트 찾기 (rnd_onboarding 패키지는 설치돼 있어 import 경로 조작 불필요)
ROOT = Path.cwd()
if not (ROOT / "pyproject.toml").exists():
    ROOT = ROOT.parent
load_dotenv(ROOT / ".env")

MODEL = "gpt-5.4-nano"
EFFORT = "low"
N = 10  # 1위~N위
print("ROOT:", ROOT, "| MODEL:", MODEL, "| TOP", N)

# %% [markdown]
# ## 2. OpenAI 버전 (web_search + 구조화 단일 호출)
#
# `text_format=BoxOffice` 로 **중첩 리스트(entries)까지 한 번에** 구조화된다.

# %%
from openai import OpenAI
from rnd_onboarding import prompts
from rnd_onboarding.schemas import BoxOffice

client = OpenAI()
msgs = prompts.render_boxoffice("v2", N)
resp = client.responses.parse(
    model=MODEL,
    tools=[{"type": "web_search"}],
    reasoning={"effort": EFFORT},
    input=[
        {"role": "system", "content": msgs["system"]},
        {"role": "user", "content": msgs["user"]},
    ],
    text_format=BoxOffice,
)
bo = resp.output_parsed
print(bo.pretty())

# %% [markdown]
# ## 3. LangChain 버전 (검색 → 구조화 2단계 체인)

# %%
from langchain_openai import ChatOpenAI
from rnd_onboarding import prompts
from rnd_onboarding.schemas import BoxOffice


def as_text(msg):
    content = msg.content
    if isinstance(content, str):
        return content
    parts = [block.get("text", "") if isinstance(block, dict) else str(block) for block in content]
    return "\n".join(part for part in parts if part)


search_llm = ChatOpenAI(
    model=MODEL, use_responses_api=True, reasoning_effort=EFFORT
).bind_tools([{"type": "web_search"}])
search_msg = search_llm.invoke(
    f"현재 대한민국 영화 박스오피스 1위부터 {N}위까지와 기준일, 출처 URL 을 "
    "웹에서 찾아 정리해줘. 영화진흥위원회(KOBIS) 기반 데이터를 우선 사용해."
)
findings = as_text(search_msg)

struct_llm = ChatOpenAI(model=MODEL, reasoning_effort=EFFORT).with_structured_output(BoxOffice)
msgs = prompts.render_boxoffice("v2", N, findings=findings)
bo = struct_llm.invoke([
    ("system", msgs["system"]),
    ("human", msgs["user"]),
])
print(bo.pretty())

# %% [markdown]
# ## 4. 정리
#
# - 비정형 검색 결과 → `BoxOffice`(중첩 리스트 `entries` + `sources`)로 구조화 성공.
# - 두 클라이언트 모두 동일 스키마 사용. OpenAI 는 단일 호출, LangChain 은 2단계 체인.
# - `sources` 로 출처를 노출 → 데이터 신뢰도를 투명하게 보여준다(정확도가 목적이 아님).
