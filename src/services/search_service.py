from src.database import images, search
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SearchService:
    def search_image_by_keyword(self, keyword: str):
        logger.info(f"按关键词搜索: keyword={keyword}")
        return search.search_by_keyword(keyword)

    def search_image_by_tag_keyword(self, category_id: int, keyword: str, logic: str = "AND"):
        logger.info(f"按标签关键词搜索: category_id={category_id}, keyword={keyword}, logic={logic}")
        return search.search_by_tags([(category_id, keyword)], logic)

    def combined_search(self, keyword: str | None, conditions: list[tuple[int, str]] | None, logic: str = "AND"):
        logger.info(f"组合搜索: keyword={keyword}, conditions={conditions}, logic={logic}")
        return search.combined_search(keyword, conditions, logic)

search_service = SearchService()