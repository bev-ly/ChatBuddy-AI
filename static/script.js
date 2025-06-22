const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const micBtn = document.getElementById("mic-btn");
const clearBtn = document.getElementById("clear-btn");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userMsg = input.value.trim();
  if (!userMsg) return;

  appendMessage("You", userMsg, "user");
  input.value = "";

  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMsg }),
  });

  const data = await res.json();
  appendMessage("ChatBuddy", data.reply, "bot");
});

function appendMessage(sender, text, type) {
  const msg = document.createElement("div");
  msg.classList.add("message", type);
  msg.innerHTML = `<strong>${sender}:</strong> <p>${text}</p>`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// 🎙️ Speech Recognition
if ("webkitSpeechRecognition" in window) {
  const recognition = new webkitSpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  micBtn.addEventListener("click", () => {
    recognition.start();
    micBtn.innerText = "🎙️ Listening...";
  });

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    input.value = transcript;
    micBtn.innerText = "🎤";
  };

  recognition.onerror = function () {
    micBtn.innerText = "🎤";
    alert("Speech recognition failed.");
  };

  recognition.onend = function () {
    micBtn.innerText = "🎤";
  };
} else {
  micBtn.disabled = true;
  micBtn.innerText = "🎤 Not supported";
}

// 🧹 Clear Chat
clearBtn.addEventListener("click", async () => {
  if (!confirm("Clear chat history?")) return;

  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "clear" }),
  });

  const data = await res.json();
  chatBox.innerHTML = "";
  appendMessage("ChatBuddy", data.reply, "bot");
});
