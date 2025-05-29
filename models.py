from pydantic import BaseModel

class ItemPdf(BaseModel):
    id: str
    name: str
    color: str
    image: str  # URL
    stock: int


class StockSize(BaseModel):
    size: int
    quantity: int

class StockColorGroup(BaseModel):
    color: str
    size: list[StockSize]
    # first: bool
    imageUrl: str
    imageName: str

class Prices(BaseModel):
    retail: float
    wholesale: float

class StockModel(BaseModel):
    id: str
    name: str
    brand: str
    prices: Prices
    category: str
    gender: str
    stockByColors: list[StockColorGroup]
