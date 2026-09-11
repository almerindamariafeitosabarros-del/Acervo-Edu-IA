from rest_framework.pagination import PageNumberPagination


class PaginacaoPadrao(PageNumberPagination):
    """Paginação de 12 itens, com o tamanho ajustável pela tela (até 100)."""

    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100
