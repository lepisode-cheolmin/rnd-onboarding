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


class BoxOfficeEntry(BaseModel):
    """박스오피스 순위 한 줄."""

    rank: int = Field(description="박스오피스 순위. 1이 1위.")
    title: str = Field(description="영화 제목.")


class BoxOffice(BaseModel):
    """박스오피스 순위 구조화 스키마 (중첩 리스트 + 출처).

    비정형 검색 결과를 순위 리스트 + 출처 URL 로 구조화한다.
    """

    country: str = Field(description="국가. 예: 대한민국.")
    as_of_date: str = Field(description="데이터 기준일. YYYY-MM-DD. 검색으로 확인된 실제 기준일.")
    entries: list[BoxOfficeEntry] = Field(description="순위 목록. rank 오름차순.")
    sources: list[str] = Field(description="정보를 가져온 실제 출처 URL 목록.")

    def pretty(self) -> str:
        """노트북에서 사람이 보기 좋게 정리한 출력 문자열."""
        lines = [f"🎬 {self.country} 박스오피스  (기준일: {self.as_of_date})"]
        for e in sorted(self.entries, key=lambda x: x.rank):
            lines.append(f"  {e.rank:>2}. {e.title}")
        lines.append("📎 출처:")
        lines.extend(f"   - {s}" for s in self.sources)
        return "\n".join(lines)
