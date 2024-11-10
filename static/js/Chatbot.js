document.addEventListener('DOMContentLoaded', function() {
    const chatbotIcon = document.getElementById('chatbot-icon');
    const chatbotContainer = document.getElementById('chatbot-container');
    const sendButton = document.getElementById('send-button');
    const messagesContainer = document.getElementById('chatbot-messages');
    const inputField = document.getElementById('chatbot-input');
    const userSearchInput = document.getElementById('user-search-input');
    const userList = document.getElementById('user-list');

    chatbotIcon.addEventListener('click', function() {
        console.log('Chatbot icon clicked'); // Debugging log
        chatbotContainer.style.display = chatbotContainer.style.display === 'block' ? 'none' : 'block';
        inputField.focus(); // Focus on the input field when opened
        userList.style.display = 'none'; // Hide user list when opened
    });


    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.textContent = `${sender}: ${message}`;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    sendButton.addEventListener('click', function() {
        const userInput = inputField.value.trim();
        if (userInput) {
            addMessage(userInput, 'You');
            inputField.value = '';

            setTimeout(() => {
                addMessage('This is a simulated response from the chatbot!', 'Bot');
            }, 1000);
        }
    });

    inputField.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendButton.click();
        }
    });

    document.getElementById('search-user-button').addEventListener('click', function() {
        const query = userSearchInput.value.trim();
        fetch(`/api/search_users?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(users => {
                userList.innerHTML = '';
                if (users.length > 0) {
                    users.forEach(user => {
                        const userElement = document.createElement('div');
                        userElement.textContent = user.nickname;
                        userElement.addEventListener('click', function() {
                            inputField.value = `Message to ${user.nickname}: `;
                            userList.style.display = 'none';
                        });
                        userList.appendChild(userElement);
                    });
                    userList.style.display = 'block';
                } else {
                    userList.style.display = 'none';
                }
            });
    });
});