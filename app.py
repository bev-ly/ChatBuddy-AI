from flask import Flask, render_template, request, jsonify
import json, os, requests, re

app = Flask(__name__)

# Memory
HISTORY_FILE = "chat_memory.json"
last_math_expr = ""
last_math_result = ""

# Load history
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# Save new chat
def save_to_history(user, bot):
    history = load_history()
    history.append({"user": user, "bot": bot})
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

# Clear memory
def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

# Math solver (free API)
def evaluate_math_api(expression):
    try:
        url = f"https://api.mathjs.org/v4/?expr={requests.utils.quote(expression)}"
        response = requests.get(url)
        return f"The answer is: {response.text}" if response.status_code == 200 else "I couldn’t compute that."
    except:
        return "There was an error solving your math expression."

# Detect math expressions
def extract_math_expression(text):
    match = re.search(r"(?:what is|calculate|solve)\s+(.+)", text)
    if match:
        return match.group(1)
    return text if re.fullmatch(r"[0-9+\-*/(). ]+", text) else None

# Dictionary definition
def define_word(word, with_example=False):
    try:
        res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        if res.status_code == 200:
            data = res.json()
            definition = data[0]["meanings"][0]["definitions"][0]["definition"]
            example = data[0]["meanings"][0]["definitions"][0].get("example", None)
            if with_example:
                return f"Example of **{word}**: {example}" if example else f"Sorry, no example found."
            return f"**{word.capitalize()}** means: {definition}\nExample: {example or 'No example available.'}"
        else:
            return f"Sorry, I couldn’t find the definition for '{word}'."
    except:
        return "There was an error with the dictionary."

@app.route("/")
def index():
    return render_template("index.html", history=load_history())

@app.route("/chat", methods=["POST"])
def chat():
    global last_math_expr, last_math_result

    user_msg = request.json.get("message", "").strip().lower()

    if not user_msg:
        return jsonify({"reply": "Please type a message."})

    # Clear memory
    if user_msg.startswith("clear"):
        clear_history()
        return jsonify({"reply": "Chat history cleared!"})

    # Definitions
    if user_msg.startswith("what is") or user_msg.startswith("define"):
        word = user_msg.replace("what is", "").replace("define", "").strip()
        reply = define_word(word)

    # Examples
    elif user_msg.startswith("example of") or "give example of" in user_msg:
        word = user_msg.replace("example of", "").replace("give example of", "").strip()
        reply = define_word(word, with_example=True)

    # Explain math logic
    elif "explain to me why" in user_msg or "why is the answer" in user_msg:
        if last_math_expr and last_math_result:
            clean_result = last_math_result.replace("The answer is: ", "").strip()

            # Try to parse and break down
            step_explanation = ""
            tokens = re.split(r"([\+\-\*/])", last_math_expr.replace(" ", ""))
            if len(tokens) == 3:
                try:
                    a, op, b = tokens
                    a_val = float(a)
                    b_val = float(b)
                    operators = {
                        "+": "plus",
                        "-": "minus",
                        "*": "multiplied by",
                        "/": "divided by"
                    }
                    step_explanation = f"`{a}` {operators[op]} `{b}` equals `{clean_result}`"
                except:
                    pass

            reply = f"""
Sure! Here's a breakdown:

🧮 **Expression:** `{last_math_expr}`  
✅ **Answer:** `{clean_result}`

{step_explanation if step_explanation else 'I used order of operations (PEMDAS) to solve this. That means: parentheses → exponents → multiplication/division → addition/subtraction.'}
""".strip()
        else:
            reply = "Please solve a math problem first, then I can explain it."

    # Solve math
    else:
        expr = extract_math_expression(user_msg)
        if expr:
            last_math_expr = expr
            last_math_result = evaluate_math_api(expr)
            reply = last_math_result
        else:
            reply = "I'm here to help with math, definitions, or explanations. Try asking me to solve or explain something!"

    save_to_history(user_msg, reply)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
