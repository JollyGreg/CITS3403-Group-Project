const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');

let lastMessageCount = 0;

//scrolls down to the bottom of the chatbox to the latest message
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

//creates and displays the message bubble with the senders name above it
function addMessage(text, sender, isSelf) {
    const wrapper = document.createElement('div');
    const senderLabel = document.createElement('div');
    senderLabel.classList.add('message-sender');
    senderLabel.textContent = sender;
    const bubble = document.createElement('div');
    //changes colour and alignment dependent on message being sent or recieved 
    bubble.classList.add('message', isSelf ? 'sent' : 'received');
    bubble.textContent = text;
    wrapper.appendChild(senderLabel);
    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
}

//polls server for new messages since last check
function pollMessages() {
    if (!gameId) return;
    fetch(`/api/game/${gameId}/messages`)
        .then(r => r.json())
        .then(msgs => {
            if (msgs.length > lastMessageCount) {
                msgs.slice(lastMessageCount).forEach(m => {
                    const isSelf = m.sender === currentUsername;
                    if (!isSelf) {
                        addMessage(m.content, m.sender, false);
                    }
                });
                lastMessageCount = msgs.length;
            }
        })
        .catch(err => console.log('Poll error:', err));
}

//sends a message to the server
function sendMessage() {
    const text = chatInput.value.trim();
    if (!text || !gameId) return;
    chatInput.value = '';
    //show your own message immediately
    addMessage(text, currentUsername, true);
    lastMessageCount++;
    fetch(`/api/game/${gameId}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text })
    }).catch(err => console.log('Send error:', err));
}

sendButton.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});

