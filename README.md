# AI Travel Planner

An AI-powered travel planning assistant that helps users plan their trips by providing flight and hotel recommendations.

## Features
- Flight search using Google Flights API
- Hotel search using Google Hotels API
- General travel information using DuckDuckGo
- Conversation memory to maintain context
- Beautiful and responsive UI

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERPAPI_API_KEY=your_serpapi_api_key
   ```

3. Run the application:
   ```bash
   python main.py
   ```

4. Open http://localhost:5000 in your browser

## Usage
Simply type your travel query in the chat interface. The AI will help you:
- Find flights between destinations
- Search for hotels
- Create travel itineraries
- Answer general travel questions

## Note
Make sure you have valid API keys for OpenAI and SerpAPI before running the application.
