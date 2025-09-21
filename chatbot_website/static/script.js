document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const themeToggle = document.getElementById("checkbox");

    // --- THEME SWITCHER LOGIC ---
    // Function to set the theme
    const setTheme = (isDarkMode) => {
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
            themeToggle.checked = true;
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            themeToggle.checked = false;
            localStorage.setItem('theme', 'light');
        }
    };

    // Event listener for the toggle switch
    themeToggle.addEventListener('change', () => {
        setTheme(themeToggle.checked);
    });

    // Check localStorage for saved theme preference on page load
    const savedTheme = localStorage.getItem('theme');
    // Default to light mode if nothing is saved or system prefers dark
    if (savedTheme === 'dark' || (savedTheme === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        setTheme(true);
    } else {
        setTheme(false);
    }

    // --- CHATBOT LOGIC ---
    let userId = sessionStorage.getItem("userId");
    if (!userId) {
        userId = self.crypto.randomUUID();
        sessionStorage.setItem("userId", userId);
    }

    // Function to add a message to the chat box
    const addMessage = (text, sender) => {
        const messageContainer = document.createElement("div");
        messageContainer.classList.add("message", sender);

        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message-text");
        
        // Basic markdown for bold text
        messageDiv.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        messageContainer.appendChild(messageDiv);
        chatBox.appendChild(messageContainer);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Function to handle sending a message
    const handleSendMessage = async () => {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, "user-message");
            userInput.value = "";

            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: message, user_id: userId }),
                });

                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }

                const data = await response.json();
                addMessage(data.response, "bot-message");

            } catch (error) {
                console.error("Error sending message:", error);
                addMessage("Sorry, I'm having trouble connecting. Please try again.", "bot-message");
            }
        }
    };

    sendBtn.addEventListener("click", handleSendMessage);
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            handleSendMessage();
        }
    });
});

