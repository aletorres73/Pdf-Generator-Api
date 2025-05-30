from pydantic import BaseModel

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
