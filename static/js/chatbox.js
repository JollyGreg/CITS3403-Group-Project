const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');

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

//fetches messages from the server and displays them
function pollMessages() {
    fetch('/api/messages')
        .then(r => r.json())
        .then(messages => {
            chatMessages.innerHTML = '';
            messages.forEach(m => {
                const isSelf = m.sender === currentUsername;
                addMessage(m.content, m.sender, isSelf);
            });
        })
        .catch(err => console.log('Poll error:', err));
}

//when the user sends a message
function sendMessage() {
    const text = chatInput.value;
    //will stop if the input of the user is empty
    if (!text) return;
    //will clear the input field after message sent
    chatInput.value = '';
    //sends the message to the server to be stored in the database
    fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text })
    })
    .then(r => r.json())
    .then(() => pollMessages())
    .catch(err => console.log('Send error:', err));
}

sendButton.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});

//start polling for new messages every 2 seconds when page loads
document.addEventListener('DOMContentLoaded', () => {
    pollMessages();
    setInterval(pollMessages, 2000);
});