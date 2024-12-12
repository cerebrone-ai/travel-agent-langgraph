from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FlightSearch(BaseModel):
    departure_id: str
    arrival_id: str
    outbound_date: str
    return_date: Optional[str] = None
    currency: str = "USD"

class HotelSearch(BaseModel):
    location: str
    check_in_date: str
    check_out_date: str
    adults: int = 2
    currency: str = "USD"

class FlightDetails(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    price: str
    duration: str

class HotelDetails(BaseModel):
    name: str
    rating: Optional[float]
    price: str
    address: str
    description: Optional[str]

class TravelPlan(BaseModel):
    query: str
    flights: Optional[List[FlightDetails]] = None
    hotels: Optional[List[HotelDetails]] = None
    itinerary: Optional[str] = None
