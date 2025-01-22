from rest_framework.pagination import PageNumberPagination


class GenericPagination(PageNumberPagination):
    page_size = 10
    # max_page_size = 30
    page_size_query_param = 'size'
    page_query_param = 'page'
    last_page_strings = ('last',)