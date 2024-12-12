from langchain.tools import BaseTool
from serpapi import GoogleSearch
from typing import Optional, Type
from schema import FlightSearch, HotelSearch
import os
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

class FlightSearchTool(BaseTool):
    name: str = "flight_search"
    description: str = "Search for flights between airports. Input should be a JSON string with departure_id, arrival_id, outbound_date, and optional return_date."
    return_direct: bool = True
    args_schema: Optional[Type] = FlightSearch

    def _run(self, departure_id: str, arrival_id: str, outbound_date: str, return_date: Optional[str] = None, currency: str = "USD"):
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "currency": currency,
            "hl": "en",
            "api_key": SERPAPI_API_KEY
        }
        if return_date:
            params["return_date"] = return_date

        search = GoogleSearch(params)
        result = search.get_dict()
        
        # Format the flight information into a readable string
        output = []
        if "best_flights" in result:
            for flight in result["best_flights"]:
                output.append(f"Flight Option - Price: ${flight.get('price', 'N/A')}")
                for leg in flight.get("flights", []):
                    dep = leg["departure_airport"]
                    arr = leg["arrival_airport"]
                    output.append(
                        f"  {dep['id']} → {arr['id']}: {dep['time']} - {arr['time']}\n"
                        f"  {leg.get('airline', 'N/A')} {leg.get('flight_number', '')}\n"
                        f"  Duration: {leg.get('duration', 'N/A')} minutes"
                    )
                output.append("")  # Empty line between flights
        
        return "\n".join(output) if output else "No flights found"

class HotelSearchTool(BaseTool):
    name: str = "hotel_search"
    description: str = "Search for hotels in a specific location. Input should be a JSON string with location, check_in_date, and check_out_date."
    return_direct: bool = True
    args_schema: Optional[Type] = HotelSearch

    def _run(self, location: str, check_in_date: str, check_out_date: str, adults: int = 2, currency: str = "USD"):
        params = {
            "engine": "google_hotels",
            "q": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "adults": str(adults),
            "currency": currency,
            "gl": "us",
            "hl": "en",
            "api_key": SERPAPI_API_KEY
        }
        search = GoogleSearch(params)
        result = search.get_dict()
        
        # Format the hotel information into a readable string
        output = []
        if "properties" in result:
            for property in result["properties"]:
                hotel_info = []
                hotel_info.append(f"Hotel: {property.get('name', 'N/A')}")
                
                if "rate_per_night" in property:
                    rate = property["rate_per_night"].get("lowest", "N/A")
                    hotel_info.append(f"Price per night: {rate}")
                
                if "total_rate" in property:
                    total = property["total_rate"].get("lowest", "N/A")
                    hotel_info.append(f"Total price: {total}")
                
                hotel_info.append(f"Rating: {property.get('overall_rating', 'N/A')}/5.0")
                hotel_info.append(f"Reviews: {property.get('reviews', 'N/A')}")
                hotel_info.append(f"Hotel Class: {property.get('hotel_class', 'N/A')}")
                hotel_info.append(f"Check-in: {property.get('check_in_time', 'N/A')}")
                hotel_info.append(f"Check-out: {property.get('check_out_time', 'N/A')}")
                
                if property.get('eco_certified'):
                    hotel_info.append("✓ Eco-certified")
                
                if "gps_coordinates" in property:
                    coords = property["gps_coordinates"]
                    hotel_info.append(f"Location: {coords.get('latitude', 'N/A')}, {coords.get('longitude', 'N/A')}")
                
                if property.get('amenities'):
                    hotel_info.append("\nAmenities:")
                    hotel_info.extend([f"- {amenity}" for amenity in property['amenities'][:5]])
                
                if "nearby_places" in property:
                    hotel_info.append("\nNearby Places:")
                    for place in property["nearby_places"][:3]:
                        place_info = [f"- {place['name']}"]
                        for transport in place.get('transportations', []):
                            place_info.append(f"  • {transport['type']}: {transport['duration']}")
                        hotel_info.extend(place_info)
                
                output.append("\n".join(hotel_info))
                output.append("")  # Empty line between hotels
        
        return "\n".join(output) if output else "No hotels found"

RESEARCH_PROMPT = """You are a friendly and enthusiastic travel agent named Alex! Your goal is to research and understand travel plans.

When a user sends a request:
1. First, analyze their needs and extract:
   - Departure city/airport
   - Destination city
   - Travel dates
   - Budget level (if mentioned)
   - Preferences (luxury, budget, adventure, etc.)

2. Use the flight_search tool to find flights between:
   - The nearest airport to the departure city and the nearest airport to the destination city
   - Return flights from the nearest airport to the destination city to the nearest airport to the departure city
3. Use the hotel_search tool to find hotels in the destination city.
4. Use the duckduckgo tool to research the destination city and provide a summary of the destination.

Important:
1. Always search for both flights AND hotels
2. Use actual prices from search results
3. Format dates as YYYY-MM-DD
4. Include specific flight numbers and hotel names
5. Add local context from DuckDuckGo searches
6. Keep the tone friendly and conversational

Remember to:
- Consider the user's stated preferences and budget
- Research both popular attractions and hidden gems
- Look up practical information about local transport and customs
"""

TRAVEL_PLAN_PROMPT = """You are a friendly and enthusiastic travel agent named Alex! Your goal is to research and understand travel plans.


RESEARCH RESULTS:
{research_results}

Now that you have researched the travel details, create a complete plan using this structure:
<div class="travel-plan">
    <h2>✈️ Your Personalized Travel Plan</h2>
    
    <div class="understanding">
        <h3>Understanding Your Trip</h3>
        <p>[Summarize their requirements and preferences]</p>
    </div>

    <div class="flights-section">
        <h3>✈️ Flight Options</h3>
        [Display researched flight options]
    </div>

    <div class="accommodation-section">
        <h3>🏨 Recommended Hotels</h3>
        [Display researched hotel options]
    </div>

    <div class="destination-guide">
        <h3>🌟 Destination Highlights</h3>
        [Share researched information about]:
        - Best time to visit
        - Must-see attractions
        - Local transportation tips
        - Restaurant recommendations
    </div>

    <div class="suggested-itinerary">
        <h3>📅 Suggested Itinerary</h3>
        [Create day-by-day plan based on flight times and attractions]
    </div>

    <div class="budget-summary">
        <h3>💰 Budget Overview</h3>
        - Flights: [Estimated cost]
        - Accommodation: [Estimated cost]
        - Activities & Food: [Estimated cost]
        - Total Estimated Cost: [Sum]
    </div>

    <div class="travel-tips">
        <h3>✨ Pro Tips</h3>
        [Share relevant travel tips for the destination]
    </div>
</div>

Important:
1. Use the research you've already gathered
2. Provide realistic daily itineraries
3. Include budget estimates for all aspects
4. Last message should be a summary of the plan

Remember to:
- Explain why you're recommending certain options
- Provide alternatives when possible
- Keep the tone friendly and conversational
"""
