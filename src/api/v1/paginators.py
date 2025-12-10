from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):
    """
    Кастомный пагинатор c возможностью задать размер
    страницы параметром запроса "limit".
    """

    page_size_query_param = "limit"
    page_size = 50
    max_page_size = 50
