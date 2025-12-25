const API_URL = "http://127.0.0.1:8000/chat";

function setupChat() {
  const form = document.getElementById("chat-form") as HTMLFormElement | null;
  const textarea = document.getElementById("user-input") as HTMLTextAreaElement | null;
  const sendButton = document.getElementById("send-button") as HTMLButtonElement | null;
  const messagesContainer = document.getElementById("chat-messages") as HTMLElement | null;
  const typingIndicator = document.getElementById("typing-indicator") as HTMLElement | null;

  if (!form || !textarea || !sendButton || !messagesContainer || !typingIndicator) {
    console.error("Chat UI elements not found in DOM");
    return;
  }

  const messagesEl = messagesContainer as HTMLElement;
  const textareaEl = textarea as HTMLTextAreaElement;
  const sendButtonEl = sendButton as HTMLButtonElement;
  const typingIndicatorEl = typingIndicator as HTMLElement;

  let isStreaming = false;

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
    window.scrollTo({
    top: document.body.scrollHeight,
    behavior: "smooth",
  });
  }

  function setUIBusy(busy: boolean) {
    isStreaming = busy;
    textareaEl.disabled = busy;
    sendButtonEl.disabled = busy;
    if (busy) {
      typingIndicatorEl.classList.remove("hidden");
    } else {
      typingIndicatorEl.classList.add("hidden");
    }
  }

  async function sendMessage(question: string) {
    const trimmed = question.trim();
    if (!trimmed || isStreaming) {
      return;
    }

 
    const userMsg = document.createElement("div");
    userMsg.className = "message user";
    userMsg.textContent = trimmed;
    messagesEl.appendChild(userMsg);
    scrollToBottom();

    textareaEl.value = "";
    setUIBusy(true);

    
    const assistantMsg = document.createElement("div");
    assistantMsg.className = "message assistant";
    assistantMsg.textContent = "";
    messagesEl.appendChild(assistantMsg);
    scrollToBottom();

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: trimmed }),
      });

      if (!response.ok || !response.body) {
        assistantMsg.textContent = "אירעה שגיאה מהשרת (status " + response.status + ").";
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done || !value) break;

        const chunk = decoder.decode(value, { stream: true });
        assistantMsg.textContent += chunk;
        scrollToBottom();
      }
    } catch (err) {
      console.error(err);
      assistantMsg.textContent = "אירעה שגיאה בחיבור לשרת.";
    } finally {
      setUIBusy(false);
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const text = textareaEl.value;
    void sendMessage(text);
  });

  textareaEl.addEventListener("keydown", (event: KeyboardEvent) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      const text = textareaEl.value;
      void sendMessage(text);
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupChat();
});
