from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Custom definitions
definitions = {
    "photosynthesis": {
        "definition": "Photosynthesis is how green plants use sunlight to make food from carbon dioxide and water.",
        "example": "For example, trees absorb sunlight to produce oxygen through photosynthesis."
    },
    "gravity": {
        "definition": "Gravity is a natural force that pulls objects toward each other — especially toward the Earth.",
        "example": "An apple falling from a tree is caused by gravity."
    },
    "algorithm": {
        "definition": "An algorithm is a step-by-step method to solve a specific problem.",
        "example": "A recipe is like an algorithm for cooking."
    },
    "python": {
        "definition": "Python is a programming language known for its readability and power.",
        "example": "Developers use Python for web apps, AI, data analysis, and more."
    }
}

# General responses for small talk
greetings = ["Hello!", "Hi there 👋", "Hey! How can I assist you today?"]
thanks = ["You're welcome!", "Glad to help 😊", "Anytime!"]
fallbacks = [
    "Hmm, I’m still learning. Try asking me to define a word or ask about a topic.",
    "Interesting! Can you ask in a different way?",
    "I didn’t quite get that. Want to try asking about a concept?"
]

# Chatbot logic
def chatbot_response(message):
    msg = message.lower().strip()

    if any(word in msg for word in ["hi", "hello", "hey"]):
        return random.choice(greetings)

    if "bye" in msg:
        return "Goodbye! 👋 Stay curious."

    if "thank" in msg:
        return random.choice(thanks)

    if "your name" in msg:
        return "I'm ChatBuddy AI — your smart assistant."

    if "how are you" in msg:
        return "I'm just a bunch of code, but I'm here and ready to help!"

    for keyword in definitions:
        if f"what is {keyword}" in msg or f"define {keyword}" in msg or f"explain {keyword}" in msg or f"what does {keyword}" in msg:
            item = definitions[keyword]
            return f"**{keyword.capitalize()}**: {item['definition']}\n\nExample: {item['example']}"

    return random.choice(fallbacks)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    bot_reply = chatbot_response(user_msg)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
