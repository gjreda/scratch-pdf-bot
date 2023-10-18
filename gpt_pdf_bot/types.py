from dataclasses import dataclass, field
from typing import Any, List, Dict


@dataclass
class Chunk:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Page:
    text: str
    page_num: int


@dataclass
class Document:
    source: str
    metadata: Dict[str, Any]
    pages: List[Page] = field(default_factory=list)
