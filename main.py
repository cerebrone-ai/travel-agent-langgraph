from datetime import datetime
from flask import Flask, render_template, request, jsonify
from langchain.schema.messages import SystemMessage, HumanMessage
from prompt import RESEARCH_PROMPT, TRAVEL_PLAN_PROMPT, FlightSearchTool, HotelSearchTool
import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()

app = Flask(__name__)

tools = [
    FlightSearchTool(),
    HotelSearchTool(),
]

memory = MemorySaver()



model = ChatOpenAI(temperature=0.7, model="gpt-4o")
agent_executor = create_react_agent(
    model,
    tools=tools,
    checkpointer=memory
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        config = {"configurable": {"thread_id": "local"}}

        research_response = agent_executor.invoke({
            "messages": [
                SystemMessage(content=RESEARCH_PROMPT),
                HumanMessage(content=f"Create a complete travel plan based on: {user_message}, Today's Date is {datetime.now().strftime('%Y-%m-%d')}")
            ]
        }, config=config)

        print("Research Response Came Back, Now Creating Plan")
        plan_response = model.invoke([
            SystemMessage(content=TRAVEL_PLAN_PROMPT.format(research_results=research_response["messages"])),
            HumanMessage(content=user_message)
        ])

        # Remove ```html tags from response content
        cleaned_response = plan_response.content.replace('```html', '')

        return jsonify({'response': cleaned_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)