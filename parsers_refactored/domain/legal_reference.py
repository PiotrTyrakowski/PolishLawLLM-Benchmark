from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class LegalReference:
    article: str
    code: str
    paragraph: Optional[str] = None
    point: Optional[str] = None
    content: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "article": self.article,
            "code": self.code,
            "paragraph": self.paragraph,
            "point": self.point,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "LegalReference":
        return cls(
            article=data["article"],
            code=data["code"],
            paragraph=data.get("paragraph"),
            point=data.get("point"),
            content=data.get("content"),
        )

    @property
    def full_reference(self) -> str:
        parts = [f"art. {self.article}"]
        if self.paragraph:
            parts.append(f"§ {self.paragraph}")
        if self.point:
            parts.append(f"pkt {self.point}")
        parts.append(self.code)
        return " ".join(parts)
