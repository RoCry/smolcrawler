import hashlib
from typing import Protocol, runtime_checkable

from loguru import logger


@runtime_checkable
class ContentDetector(Protocol):
    def is_duplicate(self, content: str) -> bool:
        """Check if content is duplicate."""
        ...

    def add_content(self, content: str) -> None:
        """Add content to the detector."""
        ...

    def clear(self) -> None:
        """Clear all tracked content."""
        ...


class HashBasedDetector(ContentDetector):
    def __init__(self):
        self.content_hashes: set[str] = set()

    def _get_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def is_duplicate(self, content: str) -> bool:
        content_hash = self._get_hash(content)
        is_dup = content_hash in self.content_hashes
        return is_dup

    def add_content(self, content: str) -> None:
        content_hash = self._get_hash(content)
        self.content_hashes.add(content_hash)

    def clear(self) -> None:
        self.content_hashes.clear()


# Future implementation for similarity detection
class SimilarityBasedDetector(ContentDetector):
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.contents: list[str] = []

    def is_duplicate(self, content: str) -> bool:
        # TODO: Implement similarity detection using libraries like difflib or fuzzywuzzy
        return False

    def add_content(self, content: str) -> None:
        self.contents.append(content)

    def clear(self) -> None:
        self.contents.clear()
