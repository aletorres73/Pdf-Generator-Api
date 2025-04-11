from pydantic import BaseModel

class ItemPdf(BaseModel):
    id: str
    name: str
    color: str
    image: str  # URL
    stock: int
