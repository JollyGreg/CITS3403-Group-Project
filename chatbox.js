const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');

//scrolls down to the bottom of the chatbox to the latest message
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

//creates and displays the message bubble with the senders name above it
function addMessage(text, type, sender) {
    const wrapper = document.createElement('div');
    const senderLabel = document.createElement('div');
    senderLabel.classList.add('message-sender');
    senderLabel.textContent = sender;
    const bubble = document.createElement('div');
    //changes colour and alignment dependent on message being sent or recieved 
    bubble.classList.add('message', type);
    bubble.textContent = text;
    wrapper.appendChild(senderLabel);
    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
}

//when the user sends a message
function sendMessage() {
    const text = chatInput.value;
    //will stop if the input of the user is empty
    if (!text) return;
    addMessage(text, 'sent', 'You');
    //will clear the input field after message sent
    chatInput.value = '';
    //will replace but just to see it work, will say "message recieved" after a second
    setTimeout(() => {
        addMessage('message received', 'received', 'Opponent');
    }, 1000);
}

sendButton.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});