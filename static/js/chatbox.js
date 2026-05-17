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
    wrapper.style.display = 'flex';
    wrapper.style.flexDirection = 'column';
    wrapper.style.alignItems = isSelf ? 'flex-end' : 'flex-start';
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

//sends a message to the server
function sendMessage() {
    const text = chatInput.value.trim();
    if (!text || !gameId) return;
    chatInput.value = '';
    addMessage(text, currentUsername, true);
    socket.emit('send_message', {
        game_id: gameId,
        sender: currentUsername,
        sender_id: currentUserId,
        content: text
    });
}

sendButton.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});

