from pydantic import BaseModel

class ItemPdf(BaseModel):
    name: str
    color: str
    image: str  # URL
    stock: int
