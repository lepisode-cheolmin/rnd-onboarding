"""프롬프트 매니징: 버전별 시스템/유저 템플릿 레지스트리.

- 프롬프트를 코드에 흩뿌리지 않고 한 곳에서 **버전으로 관리**한다.
- `$title`(영화 제목)과 `$context`(웹 검색 결과, 선택)를 끼워 넣는 **템플릿 방식**.
- 같은 입력에 v1/v2 를 바꿔 끼우며 출력 차이를 비교할 수 있다.

두 가지 흐름을 모두 지원한다:
- 단일 호출(OpenAI): 모델이 web_search 툴로 직접 검색 → findings 없이 render(title) 사용.
- 2단계(LangChain): 먼저 검색해 findings 를 얻고 → render(title, findings) 로 구조화.
"""

from string import Template

_PROMPTS: dict[str, dict[str, object]] = {
    # v1: 최소 지시 — 베이스라인
    "v1": {
        "system": "You are a film database assistant. Find the movie and return structured info.",
        "user": Template("영화 \"$title\" 의 정보를 구조화하라.$context"),
    },
    # v2: 한국어 큐레이터 — 근거 제한, 형식/길이 규칙 강화
    "v2": {
        "system": (
            "당신은 한국어 영화 정보 큐레이터다. 웹에서 찾은 사실만 근거로 사용하고 추측하지 마라. "
            "개봉일은 YYYY-MM-DD, 평점은 10점 만점 숫자, 줄거리는 2~4문장으로 작성한다."
        ),
        "user": Template(
            "영화 \"$title\" 의 정보를 한국어로 구조화해줘.\n"
            "- 배우는 주연 위주 최대 5명\n"
            "- 제작사가 여러 곳이면 대표 1곳$context"
        ),
    },
}


_BOXOFFICE_PROMPTS: dict[str, dict[str, object]] = {
    # v1: 최소 지시
    "v1": {
        "system": "You extract the current box office ranking into structured data.",
        "user": Template("현재 대한민국 박스오피스 1위부터 $n위까지를 구조화하라.$context"),
    },
    # v2: KOBIS 우선, 기준일/출처 강제
    "v2": {
        "system": (
            "당신은 한국 박스오피스 데이터를 구조화하는 큐레이터다. 웹에서 찾은 사실만 근거로 사용하고 "
            "추측하지 마라. 가능하면 영화진흥위원회(KOBIS) 기반 데이터를 우선 사용한다. "
            "entries 는 rank 오름차순, as_of_date(기준일)와 sources(실제 참고 URL)를 반드시 채운다."
        ),
        "user": Template(
            "현재 대한민국 영화 박스오피스 순위 1위부터 $n위까지를 구조화해줘.\n"
            "- 제목은 한국어\n"
            "- sources 에는 실제로 참고한 URL 을 넣을 것$context"
        ),
    },
}


def list_versions() -> list[str]:
    """등록된 프롬프트 버전 목록."""
    return list(_PROMPTS)


def render_boxoffice(version: str, n: int = 10, findings: str = "") -> dict[str, str]:
    """박스오피스 프롬프트 렌더링. findings 가 있으면 [검색 결과] 블록을 덧붙인다."""
    if version not in _BOXOFFICE_PROMPTS:
        raise KeyError(f"알 수 없는 프롬프트 버전: {version}. 가능: {list(_BOXOFFICE_PROMPTS)}")
    p = _BOXOFFICE_PROMPTS[version]
    context = f"\n\n[검색 결과]\n{findings}" if findings else ""
    return {
        "system": p["system"],
        "user": p["user"].substitute(n=n, context=context),
    }


def render(version: str, title: str, findings: str = "") -> dict[str, str]:
    """버전/제목/(선택)검색결과로 {system, user} 메시지를 만든다.

    findings 가 주어지면 user 프롬프트 끝에 [검색 결과] 블록으로 덧붙인다.
    """
    if version not in _PROMPTS:
        raise KeyError(f"알 수 없는 프롬프트 버전: {version}. 가능: {list_versions()}")
    p = _PROMPTS[version]
    context = f"\n\n[검색 결과]\n{findings}" if findings else ""
    return {
        "system": p["system"],
        "user": p["user"].substitute(title=title, context=context),
    }
