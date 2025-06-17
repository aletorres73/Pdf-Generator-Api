from pydantic import BaseModel
from typing import Optional

class StockSize(BaseModel):
    size: int
    quantity: int

class StockColorGroup(BaseModel):
    color: str
    size: list[StockSize]
    # first: bool
    imageUrl: str
    imageName: str
    imageBase64: Optional[str] = None
                           
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
