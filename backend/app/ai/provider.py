from abc import ABC, abstractmethod


class AIAnalysisProvider(ABC):
    @abstractmethod
    async def analyze_product(self, product: dict) -> str: ...

    @abstractmethod
    async def analyze_note(self, note: dict) -> str: ...

    @abstractmethod
    async def summarize_daily_report(self, report: dict) -> str: ...


class MockAIProvider(AIAnalysisProvider):
    async def analyze_product(self, product: dict) -> str:
        return f"mock product analysis for {product.get('product_name')}"

    async def analyze_note(self, note: dict) -> str:
        return f"mock note analysis for {note.get('title')}"

    async def summarize_daily_report(self, report: dict) -> str:
        return f"mock daily summary notes={report.get('new_notes')} products={report.get('new_products')}"
