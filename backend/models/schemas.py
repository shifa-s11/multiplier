from pydantic import BaseModel


class RevenuePoint(BaseModel):
    label: str
    revenue: float


class TopCustomer(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    revenue: float
