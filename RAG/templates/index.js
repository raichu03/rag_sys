const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const socket = new WebSocket('ws://127.0.0.1:8000/chat');

socket.onopen = () => {
    console.log('Connection established');
};

function sendMessage() {
    const messageText = messageInput.value.trim();
    console.log("hi")
    if (messageText) {
        const messageRow = document.createElement('div');
        messageRow.classList.add('message-row-end');

        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('message-bubble', 'user');
        bubbleDiv.textContent = messageText;

        messageRow.appendChild(bubbleDiv);
        chatMessages.appendChild(messageRow);

        chatMessages.scrollTop = chatMessages.scrollHeight;

        messageInput.value = '';

        setTimeout(() => {
            LLMResponse(messageText);
        }, 1000);
    }
}

async function LLMResponse(userMessage) {
    const message = {
        "query": userMessage
    };
    socket.send(JSON.stringify(message));

    socket.onmessage = (event) => {
        try {
            const response = JSON.parse(event.data);
            const responseText = response.message

            const messageRow = document.createElement('div');
            messageRow.classList.add('message-row-start');

            const bubbleDiv = document.createElement('div');
            bubbleDiv.classList.add('message-bubble', 'llm');
            bubbleDiv.textContent = responseText;

            messageRow.appendChild(bubbleDiv);
            chatMessages.appendChild(messageRow);

            chatMessages.scrollTop = chatMessages.scrollHeight;

        } catch (e) {
            console.error('Error parsing JSON from WebSocket message:', e);
            console.log('Received data was not valid JSON:', event.data);
        }
    };
}

window.onload = () => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
};