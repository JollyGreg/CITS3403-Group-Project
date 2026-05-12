function toggleChat() {
    const panel = document.getElementById('chatPanel');
    const btn = document.getElementById('chatToggleBtn');
    panel.classList.toggle('hidden');
    btn.style.display = panel.classList.contains('hidden') ? 'block' : 'none';
}
