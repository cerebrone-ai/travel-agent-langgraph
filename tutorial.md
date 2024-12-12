
# Step-by-Step Guide to Building an AI Travel Agent Using Flask, LangChain, LangGraph, and OpenAI GPT-4

This guide will walk you through building an AI-powered Travel Agent using Flask for the backend, LangChain for natural language processing, LangGraph for agent management, and OpenAI GPT-4 for generating detailed responses. The agent helps users plan trips by providing flight options, hotel recommendations, and travel tips.

---

## Prerequisites

### 1. Python Environment
Make sure you have Python 3.8 or later installed.

### 2. Install Required Libraries
Install the following libraries using pip:
```bash
pip install flask langchain langgraph openai python-dotenv serpapi
```

### 3. API Keys
Sign up and obtain the following API keys:
- **OpenAI API Key**: [Get it here](https://platform.openai.com/overview).
- **SerpAPI Key**: [Get it here](https://serpapi.com/).

### 4. .env File
Create a `.env` file in your project directory to securely store your API keys:
```plaintext
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_api_key
```

---

## Project Structure

Here’s the recommended project structure:

```
.
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── script.js
├── prompt.py
├── .env
└── requirements.txt
```

---

## Step 1: Flask Setup

### Create the `app.py` File
Start by setting up a basic Flask app:
```python
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    # Logic for processing user input and generating responses
    pass

if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

Run the Flask app:
```bash
python app.py
```

Visit `http://127.0.0.1:5001` to confirm the app is running.

---

## Step 2: AI Model Integration

### Load Environment Variables
Use `python-dotenv` to load API keys from the `.env` file:
```python
import os
from dotenv import load_dotenv

load_dotenv()
```

### Define AI Model and Memory
Set up LangGraph with LangChain to create an AI agent:
```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.schema.messages import SystemMessage, HumanMessage

tools = []  # Tools will be added in Step 3
memory = MemorySaver()

model = ChatOpenAI(temperature=0.7, model="gpt-4o")
agent_executor = create_react_agent(
    model,
    tools=tools,
    checkpointer=memory
)
```

---

## Step 3: Creating Travel Tools

### Flight Search Tool
Define a tool to search for flights using SerpAPI:
```python
from langchain.tools import BaseTool
from serpapi import GoogleSearch
from typing import Optional, Type
from schema import FlightSearch

class FlightSearchTool(BaseTool):
    name = "flight_search"
    description = "Search for flights between airports."

    def _run(self, departure_id: str, arrival_id: str, outbound_date: str, return_date: Optional[str] = None):
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "api_key": os.getenv("SERPAPI_API_KEY")
        }
        search = GoogleSearch(params)
        return search.get_dict()
```

### Hotel Search Tool
Similarly, define a tool for searching hotels:
```python
class HotelSearchTool(BaseTool):
    name = "hotel_search"
    description = "Search for hotels in a specific location."

    def _run(self, location: str, check_in_date: str, check_out_date: str):
        params = {
            "engine": "google_hotels",
            "q": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "api_key": os.getenv("SERPAPI_API_KEY")
        }
        search = GoogleSearch(params)
        return search.get_dict()
```

Add these tools to the `tools` list:
```python
tools = [FlightSearchTool(), HotelSearchTool()]
```

---

## Step 4: Define Prompts

### Research Prompt
Define the research prompt in a separate `prompt.py` file:

### Travel Plan Prompt
Define the travel plan prompt in a separate `prompt.py` file:

---

## Step 5: Chat API Logic

Implement the `/api/chat` endpoint in `app.py`:
```python
from prompt import RESEARCH_PROMPT, TRAVEL_PLAN_PROMPT

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        research_response = agent_executor.invoke({
            "messages": [
                SystemMessage(content=RESEARCH_PROMPT),
                HumanMessage(content=user_message)
            ]
        })

        plan_response = model.invoke([
            SystemMessage(content=TRAVEL_PLAN_PROMPT.format(research_results=research_response)),
            HumanMessage(content=user_message)
        ])

        return jsonify({'response': plan_response.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Step 6: Frontend Development

### HTML Template
Create `templates/index.html` for the user interface:
```html
<!DOCTYPE html>
<html>
<head>
    <title>AI Travel Planner</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss/dist/tailwind.min.css" rel="stylesheet">
</head>
<body>
    <div id="chat-container">
        <h1>AI Travel Planner</h1>
        <input id="user-input" type="text" placeholder="Enter your travel query">
        <button onclick="sendMessage()">Send</button>
        <div id="chat-output"></div>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
```

### JavaScript for Interactivity
Add `static/script.js` to handle chat interactions:
```javascript
async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
    });
    const data = await response.json();
    document.getElementById('chat-output').innerText = data.response || data.error;
}
```

---

## Step 7: Testing and Running the App

1. **Start Flask App**:
   ```bash
   python app.py
   ```
2. **Access the App**: Open `http://127.0.0.1:5001` in your browser.
3. **Test Queries**: Enter travel-related queries and see responses.

---


## Conclusion

You’ve successfully built an AI Travel Agent! Enhance it further by:
- Adding features like car rentals or travel insurance.
- Improving the UI/UX.
- Optimizing prompts for better responses.
