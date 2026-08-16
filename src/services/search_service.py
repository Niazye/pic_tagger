from src.database.repository import images, search

class SearchService:
    def search_image_by_keyword(self, keyword: str):
        return search.search_by_keyword(keyword)

    def search_image_by_tag_keyword(self, category_id: int, keyword: str, logic: str = "AND"):
        return search.search_by_tags([(category_id, keyword)], logic)

    def combined_search(self, keyword: str | None, conditions: list[tuple[int, str]] | None, logic: str = "AND"):
        return search.combined_search(keyword, conditions, logic)

search_service = SearchService()