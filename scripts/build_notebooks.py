"""nbformat 으로 두 버전(OpenAI / LangChain) 노트북을 생성한다.

데이터 소스: OpenAI 내장 web_search 툴 (별도 검색 키 불필요, OPENAI_API_KEY 만 필요).
- OpenAI 버전 : responses.parse(tools=[web_search], text_format=Movie) — 검색+구조화 단일 호출
- LangChain 버전: bind_tools([web_search]) 로 검색 → with_structured_output(Movie) 로 구조화 (2단계 체인)

재생성: uv run python scripts/build_notebooks.py
"""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "notebooks"
NB_DIR.mkdir(exist_ok=True)

# 공통: 경로/환경 설정 셀
SETUP = '''\
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트(schemas.py 가 있는 곳)를 import 경로에 추가
ROOT = Path.cwd()
if not (ROOT / "schemas.py").exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

TITLE = "인터스텔라"  # ← 원하는 영화 제목으로 변경
MODEL = "gpt-5.4-nano"  # web_search + structured output 지원
EFFORT = "low"          # reasoning effort (low: 빠르고 저렴)
print("ROOT:", ROOT, "| TITLE:", TITLE, "| MODEL:", MODEL, "| effort:", EFFORT)'''


def build_openai():
    nb = nbf.v4.new_notebook()
    cells = [
        nbf.v4.new_markdown_cell(
            "# 영화 정보 구조화 — OpenAI 클라이언트 버전\n\n"
            "영화 제목 입력 → **OpenAI 내장 web_search 툴로 검색** → **Structured Output**으로 "
            "공통 `Movie` 스키마에 맞춰 구조화한다.\n\n"
            "`responses.parse(tools=[web_search], text_format=Movie)` 한 번의 호출로 "
            "**검색과 구조화가 동시에** 일어난다.\n\n"
            "> 사전 준비: `.env` 에 `OPENAI_API_KEY` 만 있으면 된다 (검색 키 불필요). 실행: `uv run jupyter lab`."
        ),
        nbf.v4.new_markdown_cell("## 1. 환경 설정"),
        nbf.v4.new_code_cell(SETUP),
        nbf.v4.new_markdown_cell(
            "## 2. 검색 + 구조화 (단일 호출)\n\n"
            "`tools=[{\"type\": \"web_search\"}]` 로 모델이 직접 웹을 검색하고, "
            "`text_format=Movie` 로 결과를 `Movie` 스키마에 맞춰 돌려준다."
        ),
        nbf.v4.new_code_cell(
            'from openai import OpenAI\n'
            'import prompts\n'
            'from schemas import Movie\n\n'
            'client = OpenAI()\n\n'
            'msgs = prompts.render("v2", TITLE)  # findings 없음 → 모델이 web_search 로 직접 검색\n'
            'resp = client.responses.parse(\n'
            '    model=MODEL,\n'
            '    tools=[{"type": "web_search"}],\n'
            '    reasoning={"effort": EFFORT},\n'
            '    input=[\n'
            '        {"role": "system", "content": msgs["system"]},\n'
            '        {"role": "user", "content": msgs["user"]},\n'
            '    ],\n'
            '    text_format=Movie,\n'
            ')\n'
            'movie = resp.output_parsed\n'
            'print(movie.pretty())'
        ),
        nbf.v4.new_markdown_cell(
            "## 3. 프롬프트 매니징 — v1 vs v2 비교\n\n"
            "같은 영화에 프롬프트 버전만 바꿔 끼우며 출력 차이를 비교한다 (`prompts` 모듈이 버전 관리)."
        ),
        nbf.v4.new_code_cell(
            'for v in prompts.list_versions():\n'
            '    msgs = prompts.render(v, TITLE)\n'
            '    resp = client.responses.parse(\n'
            '        model=MODEL,\n'
            '        tools=[{"type": "web_search"}],\n'
            '        reasoning={"effort": EFFORT},\n'
            '        input=[\n'
            '            {"role": "system", "content": msgs["system"]},\n'
            '            {"role": "user", "content": msgs["user"]},\n'
            '        ],\n'
            '        text_format=Movie,\n'
            '    )\n'
            '    print(f"=== prompt {v} ===")\n'
            '    print(resp.output_parsed.model_dump_json(indent=2))\n'
            '    print()'
        ),
        nbf.v4.new_markdown_cell(
            "## 4. 정리\n\n"
            "- OpenAI Responses API 는 **툴 사용(web_search) + 구조화 출력(text_format)** 을 한 호출에 융합한다.\n"
            "- 반환 `resp.output_parsed` 가 곧 `Movie` 인스턴스 → 후처리 불필요.\n"
            "- LangChain 버전(`02_langchain_version.ipynb`)은 같은 일을 2단계 체인으로 한다 — 비교해 볼 것."
        ),
    ]
    nb.cells = cells
    nb.metadata["language_info"] = {"name": "python"}
    nbf.write(nb, NB_DIR / "01_openai_version.ipynb")


def build_langchain():
    nb = nbf.v4.new_notebook()
    cells = [
        nbf.v4.new_markdown_cell(
            "# 영화 정보 구조화 — LangChain 클라이언트 버전\n\n"
            "영화 제목 입력 → **web_search 툴로 검색**(`bind_tools`) → **Structured Output**"
            "(`with_structured_output`)으로 공통 `Movie` 스키마에 맞춰 구조화한다.\n\n"
            "OpenAI 버전과 **동일한 스키마/프롬프트**를 공유한다. 다른 점은 흐름을 **2단계 체인**으로 나눈 것."
        ),
        nbf.v4.new_markdown_cell("## 1. 환경 설정"),
        nbf.v4.new_code_cell(SETUP),
        nbf.v4.new_markdown_cell(
            "## 2. 1단계 — web_search 툴로 검색\n\n"
            "내장 툴 `{\"type\": \"web_search\"}` 를 bind 하면 LangChain 이 자동으로 "
            "Responses API 로 전환해 서버측에서 검색을 수행한다. 결과 텍스트(findings)를 얻는다."
        ),
        nbf.v4.new_code_cell(
            'from langchain_openai import ChatOpenAI\n'
            'import prompts\n'
            'from schemas import Movie\n\n\n'
            'def as_text(msg):\n'
            '    """AIMessage.content(문자열 또는 블록 리스트)를 평범한 텍스트로 변환."""\n'
            '    c = msg.content\n'
            '    if isinstance(c, str):\n'
            '        return c\n'
            '    parts = [b.get("text", "") if isinstance(b, dict) else str(b) for b in c]\n'
            '    return "\\n".join(p for p in parts if p)\n\n\n'
            'search_llm = ChatOpenAI(\n'
            '    model=MODEL, use_responses_api=True, reasoning_effort=EFFORT\n'
            ').bind_tools([{"type": "web_search"}])\n'
            'search_msg = search_llm.invoke(\n'
            '    f"영화 \'{TITLE}\' 의 개봉일, 배급사/제작사, 감독, 주요 출연진, 줄거리, 평점을 웹에서 찾아 정리해줘."\n'
            ')\n'
            'findings = as_text(search_msg)\n'
            'print(findings)'
        ),
        nbf.v4.new_markdown_cell(
            "## 3. 2단계 — 구조화\n\n"
            "검색 결과(findings)를 `with_structured_output(Movie)` 로 스키마에 맞춰 구조화한다."
        ),
        nbf.v4.new_code_cell(
            'struct_llm = ChatOpenAI(model=MODEL, reasoning_effort=EFFORT).with_structured_output(Movie)\n\n'
            'msgs = prompts.render("v2", TITLE, findings=findings)\n'
            'movie = struct_llm.invoke([\n'
            '    ("system", msgs["system"]),\n'
            '    ("human", msgs["user"]),\n'
            '])\n'
            'print(movie.pretty())'
        ),
        nbf.v4.new_markdown_cell(
            "## 4. 프롬프트 매니징 — v1 vs v2 비교\n\n"
            "검색은 한 번만 하고(findings 재사용), 구조화 프롬프트만 v1/v2 로 바꿔 비교한다."
        ),
        nbf.v4.new_code_cell(
            'for v in prompts.list_versions():\n'
            '    msgs = prompts.render(v, TITLE, findings=findings)\n'
            '    m = struct_llm.invoke([\n'
            '        ("system", msgs["system"]),\n'
            '        ("human", msgs["user"]),\n'
            '    ])\n'
            '    print(f"=== prompt {v} ===")\n'
            '    print(m.model_dump_json(indent=2))\n'
            '    print()'
        ),
        nbf.v4.new_markdown_cell(
            "## 5. 정리\n\n"
            "- LangChain 은 **검색(`bind_tools`) → 구조화(`with_structured_output`)** 를 2단계 체인으로 구성.\n"
            "- OpenAI 버전과 동일 스키마 → 결과 구조가 같다. 차이는 흐름의 추상화 방식.\n"
            "- 2단계로 나누면 검색 결과를 재사용하거나 중간에 가공하기 쉽다(프롬프트 비교처럼)."
        ),
    ]
    nb.cells = cells
    nb.metadata["language_info"] = {"name": "python"}
    nbf.write(nb, NB_DIR / "02_langchain_version.ipynb")


if __name__ == "__main__":
    build_openai()
    build_langchain()
    print("notebooks generated:", [p.name for p in NB_DIR.glob("*.ipynb")])
