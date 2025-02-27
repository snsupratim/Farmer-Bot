from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
import textwrap

# Load environment variables
load_dotenv()
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

if not GOOGLE_GEMINI_API_KEY:
    raise ValueError("API_KEY is not set in .env file!")

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/chat": {"origin": "*"}})

# Initialize LangChain components
memory = ConversationBufferMemory(memory_key="chat_history", return_message=True)
gemini_chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GOOGLE_GEMINI_API_KEY)

# System prompt to set AI behavior
SYSTEM_PROMPT = "Act as my personal agriculture AI agent. Provide expert guidance on farming, crop management, pest control, and sustainable practices."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        chat_history = memory.chat_memory.messages

        # If it's the first message, activate the AI agent prompt
        if not chat_history:
            full_message = f"{SYSTEM_PROMPT}\n\nUser: {message}"
        else:
            full_message = message

        response = gemini_chat.invoke(full_message)
        bot_reply = response.content.strip()
        
        # Format response for better readability
        formatted_reply = textwrap.fill(bot_reply, width=80)
        formatted_reply = formatted_reply.replace("**", "").replace("*", "• ")

        # Update memory with the conversation context
        memory.save_context({"input": message}, {"output": formatted_reply})

        return jsonify({"reply": formatted_reply})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Failed to fetch response"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
