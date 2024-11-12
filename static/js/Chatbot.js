document.addEventListener('DOMContentLoaded', function() {
    const chatbotIcon = document.getElementById('chatbot-icon');
    const chatbotContainer = document.getElementById('chatbot-container');
    const sendButton = document.getElementById('send-button');
    const messagesContainer = document.getElementById('chatbot-messages');
    const inputField = document.getElementById('chatbot-input');
    const userSearchInput = document.getElementById('user-search-input');
    const userList = document.getElementById('user-list');
    const socket = io.connect('http://127.0.0.1:5000');

    // Debounce timer for user search
    let debounceTimer;
    userSearchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            document.getElementById('search-user-button').click();
        }, 300); // 300ms debounce delay
    });

    // Toggle chatbot visibility
    chatbotIcon.addEventListener('click', function() {
        console.log('Chatbot icon clicked'); // Debugging log

        // Toggle display for chatbot container
        if (chatbotContainer.style.display === 'block') {
            chatbotContainer.style.display = 'none';
        } else {
            chatbotContainer.style.display = 'block';
            inputField.focus(); // Focus on the input field when opened
            userList.style.display = 'none'; // Hide user list when opened
        }
    });

    // Ensure that the chatbot container is visible when clicking the icon
    chatbotContainer.style.display = 'block'; // Ensure it's visible by default


    // Function to add a message to the chat
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.textContent = `${sender}: ${message}`;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // WebSocket listener for new messages
    socket.on('new_message', (data) => {
        // Display the new message in the chat UI when received
        console.log('New message from:', data.sender); // Debugging log
        addMessage(data.message, data.sender); // Use addMessage to display in chat
    });

    // Function to simulate sending a message to the receiver
    function sendMessageToReceiver(message) {
        // Simulate that the receiver has received a message
        setTimeout(() => {
            addMessage(message, 'Receiver');
        }, 1000); // Adjust the timeout for receiver response delay
    }

    // Send button click event
    sendButton.addEventListener('click', function() {
        const userInput = inputField.value.trim();
        if (userInput) {
            addMessage(userInput, 'You');
            inputField.value = ''; // Clear input field
            // Emit the message to the WebSocket server to forward to the recipient
            socket.emit('send_message', { message: userInput, receiver: 'receiver_username' });

        }
    });

    // Send message on Enter key press
    inputField.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendButton.click();
        }
    });

    // Add this script to your HTML or external JS file
    document.getElementById('chatbot-toggle-btn').addEventListener('click', function() {
        var iframe = document.getElementById('chatbot-frame');
        // Toggle the visibility of the iframe
        iframe.classList.toggle('hidden');
    });


    // Search users when Search button is clicked
    document.getElementById('search-user-button').addEventListener('click', function() {
        const query = userSearchInput.value.trim();
        fetch(`/api/search_users?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(users => {
                userList.innerHTML = ''; // Clear previous results
                if (users.length > 0) {
                    users.forEach(user => {
                        const userElement = document.createElement('div');
                        userElement.textContent = user.nickname;
                        userElement.addEventListener('click', function() {
                            inputField.value = `Message to ${user.nickname}: `;
                            userList.style.display = 'none'; // Hide user list after selection
                        });
                        userList.appendChild(userElement);
                    });
                    userList.style.display = 'block'; // Show user list
                } else {
                    userList.style.display = 'none'; // Hide if no users found
                }
            })
            .catch(error => {
                console.error('Error fetching users:', error);
                alert('Unable to fetch users. Please try again later.');
            });
    });

    // Prevent API call when search input is empty
    userSearchInput.addEventListener('input', function() {
        const query = userSearchInput.value.trim();
        if (query) {
            fetch(`/api/search_users?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(users => {
                    userList.innerHTML = ''; // Clear previous results
                    if (users.length > 0) {
                        users.forEach(user => {
                            const userElement = document.createElement('div');
                            userElement.textContent = user.nickname;
                            userElement.addEventListener('click', function() {
                                inputField.value = `Message to ${user.nickname}: `;
                                userList.style.display = 'none'; // Hide user list after selection
                            });
                            userList.appendChild(userElement);
                        });
                        userList.style.display = 'block'; // Show user list
                    } else {
                        userList.style.display = 'none'; // Hide if no users found
                    }
                })
                .catch(error => {
                    console.error('Error fetching users:', error);
                    alert('Unable to fetch users. Please try again later.');
                });
        } else {
            userList.style.display = 'none'; // Hide user list if query is empty
        }
    });
});