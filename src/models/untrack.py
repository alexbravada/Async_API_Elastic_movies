from fastapi import Query
from pydantic import BaseModel


class PaginatedModel(BaseModel):
    page_number: Optional[int] = Query(default=1,
                                    ge=1, # greater than or equal
                                    alias='page[number]',
                                    description='Page number.')

    page_size: Optional[int] = Query(default=50,
                                     ge=1, # greater than or equal
                                     le=100, # less than or equal
                                     alias='page[size]',
                                     description='Page size.')


class PaginateModel:  # for python 3.10 and above
    def __init__(
        self,
        page_size: int
        | None = Query(10, alias='page[size]', description='Items amount on page', ge=1),
        page_number: int
        | None = Query(
            1, alias='page[number]', description='Page number for pagination', ge=1
        ),
    ):
        self.page_number = page_number
        self.page_size = page_size

 
@router.get('/',)
async def get_list(pagination: PaginateModel = Depends(), ):
    pass
    # тутможнонработать с_pagination
