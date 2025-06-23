const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');

    function sendMessage() {
        const messageText = messageInput.value.trim();

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
                simulateLLMResponse(messageText);
            }, 1000);
        }
    }

    async function simulateLLMResponse(userMessage) {
        let responseText = "I'm sorry, I don't have enough information to respond to that.";

        const data = {query: "this is test"}

        url = 'http://127.0.0.1:8000/initial'
        const response = await fetch( url,{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },

            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const result = await response.json(); // Assuming your backend might return a JSON response
        console.log('Success:', result);

        const messageRow = document.createElement('div');
        messageRow.classList.add('message-row-start'); // LLM messages align left

        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('message-bubble', 'llm');
        bubbleDiv.textContent = responseText;

        messageRow.appendChild(bubbleDiv);
        chatMessages.appendChild(messageRow);

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    window.onload = () => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };