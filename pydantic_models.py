from pydantic import BaseModel

class NewOrderRequest(BaseModel):
    action: str
    symbol: str
    direction: str
    volume: float