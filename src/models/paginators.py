from typing import Optional

from fastapi import Query


class PaginateModel:
    def __init__(
        self,
        page_size: Optional[int] = Query(
            default=50,
            ge=1,  # greater than or equal
            le=100,  # less than or equal
            alias='page[size]',
            description='Items amount on page.',
        ),
        page_number: Optional[int] = Query(
            default=1,
            ge=1,  # greater than or equal
            alias='page[number]',
            description='Page number for pagination.',
        ),
    ):
        self.page_number = page_number
        self.page_size = page_size
        self.limit = page_size
        self.offset = (self.limit * self.page_number) - self.page_size

    def paginate_list(self, obj: list):
        stop = self.limit * self.page_number
        start = stop - self.limit
        return obj[start:stop]

    def get_max_page(self, obj: list):
        value = len(obj) / self.limit
        if value % 2 == 0.0:
            return value
        else:
            return int(value) + 1
