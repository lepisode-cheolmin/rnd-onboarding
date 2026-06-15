"""공통 구조화 출력 스키마.

OpenAI 버전과 LangChain 버전이 **동일한 Pydantic 모델**을 공유한다.
필드 description 은 LLM 의 structured output 생성 시 힌트로 사용된다.
"""

from pydantic import BaseModel, Field


class Movie(BaseModel):
    """영화 정보 구조화 스키마 (7개 필드)."""

    title: str = Field(description="영화명. 한국어 제목 우선, 없으면 원제.")
    release_date: str = Field(description="개봉일. YYYY-MM-DD 형식.")
    production: str = Field(description="배급사 또는 제작사. 여러 곳이면 대표 1곳.")
    director: str = Field(description="감독명.")
    cast: list[str] = Field(description="주요 출연 배우. 주연 위주 최대 5명.")
    synopsis: str = Field(description="줄거리 요약. 2~4문장.")
    rating: float = Field(description="평점. 10점 만점 숫자.")

    def pretty(self) -> str:
        """노트북에서 사람이 보기 좋게 정리한 출력 문자열."""
        return "\n".join(
            [
                f"🎬 {self.title}  ({self.release_date})",
                f"⭐ 평점      : {self.rating}",
                f"🎥 감독      : {self.director}",
                f"🏢 제작/배급 : {self.production}",
                f"👥 출연      : {', '.join(self.cast)}",
                f"📖 줄거리    : {self.synopsis}",
            ]
        )
