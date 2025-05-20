# scraper/core/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable

class BaseScraper(ABC):
    def __init__(self, max_pages: int = 50, headers: Optional[Dict[str, str]] = None):
        self.max_pages = max_pages
        self.headers = headers or {}

    @abstractmethod
    async def crawl(
        self,
        start_url: str,
        status_key: Optional[str] = None,
        status_callback: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        pass
