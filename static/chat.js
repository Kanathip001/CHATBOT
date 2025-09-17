function sendMessage() {
    let inputBox = document.getElementById("userInput");
    let message = inputBox.value.trim();
    if (!message) return;

    let chatbox = document.getElementById("chatbox");
    chatbox.innerHTML += `<div class="user-message">${message}</div>`;
    inputBox.value = "";
    chatbox.scrollTop = chatbox.scrollHeight;

    fetch("/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: message })
    })
    .then(res => res.json())
    .then(data => {
        chatbox.innerHTML += `<div class="bot-message">${data.reply}</div>`;
        chatbox.scrollTop = chatbox.scrollHeight;
    });
}
