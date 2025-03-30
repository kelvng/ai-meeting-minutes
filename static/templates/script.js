const sessionId = generateSessionId();
console.log("Session ID:", sessionId);

function generateSessionId() {
  return Math.random().toString(36).substr(2, 9);
}

const apiKeyForm = document.getElementById('apiKeyForm');
const apiKeyInput = document.getElementById('apiKey');
const errorMessage = document.getElementById('errorMessage');
const fileInput = document.getElementById('fileInput');
const fileErrorMessage = document.getElementById('fileErrorMessage');
const uploadedFilesElement = document.getElementById('uploadedFiles');
const chatInput = document.getElementById('chatInput');
const sendQuestionButton = document.getElementById('sendQuestionButton');
const chatMessages = document.getElementById('chatMessages');
const summarizeButton = document.getElementById('summarizeButton');

function showSuccessMessage(message) {
    const successMessageElement = document.createElement('div');
    successMessageElement.classList.add('success-message');
    successMessageElement.textContent = message;

    const sidebar = document.querySelector('.sidebar');
    sidebar.insertBefore(successMessageElement, sidebar.firstChild);

    setTimeout(() => {
        if (successMessageElement.parentNode) {
            successMessageElement.parentNode.removeChild(successMessageElement);
        }
    }, 5000);
}

// Hiển thị thông báo lỗi trong sidebar
function showErrorMessage(message) {
    errorMessage.textContent = message;
}

// Hiển thị thông báo lỗi file
function showFileErrorMessage(message) {
    fileErrorMessage.textContent = message;
}

// Hiển thị danh sách file đã upload
function appendUploadedFile(file) {
    const fileName = document.createElement('div');
    fileName.textContent = file.name;
    uploadedFilesElement.appendChild(fileName);
}

// Hàm hiển thị tin nhắn dạng Markdown trong ô chat
function displayMarkdownMessage(markdownContent, className) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', className);
    // Chuyển đổi Markdown sang HTML bằng marked
    messageElement.innerHTML = marked.parse(markdownContent);
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hàm hiển thị tin nhắn thông thường
function displayMessage(message, className) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', className);
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hiển thị chỉ báo "Assistant is typing..."
function displayTypingIndicator() {
    const typingIndicator = document.createElement('div');
    typingIndicator.classList.add('chat-message');
    typingIndicator.innerHTML = 'Assistant is typing<span class="typing-animation">...</span>';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Loại bỏ chỉ báo "Assistant is typing..."
function removeTypingIndicator() {
    const typingIndicators = document.querySelectorAll('.typing-indicator');
    typingIndicators.forEach(indicator => {
        if (indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    });
}

apiKeyForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
        showErrorMessage('Please enter an API key');
        return;
    }
    sendApiKey(apiKey);
});

function sendApiKey(apiKey) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api_key', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = () => {
        if (xhr.status === 200) {
            showSuccessMessage('API Key sent successfully.');
        } else {
            showErrorMessage('Error sending API Key: ' + xhr.statusText);
        }
    };
    xhr.onerror = () => {
        showErrorMessage('Network error occurred while sending API Key');
    };
    // Gửi kèm sessionId (sử dụng tên key "collection" để khớp với API của bạn)
    xhr.send(JSON.stringify({ api_key: apiKey, collection: sessionId }));
}

fileInput.addEventListener('change', () => {
    const files = fileInput.files;
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (file) {
            if (file.size > 2 * 1024 * 1024) {
                showFileErrorMessage('File size exceeds 2MB limit');
                continue;
            }
            uploadFile(file);
        }
    }
});

function showUploadingIndicator(fileName) {
    const indicator = document.createElement('div');
    indicator.classList.add('uploading-indicator');
    // Nếu fileName quá dài, rút gọn nó
    const maxFileNameLength = 20;
    const truncatedFileName = fileName.length > maxFileNameLength
      ? fileName.substring(0, maxFileNameLength) + '...'
      : fileName;
    indicator.textContent = `Uploading .. ${truncatedFileName}...`;
    uploadedFilesElement.appendChild(indicator);
    return indicator;
}

function uploadFile(file) {
    // Hiển thị hiệu ứng chờ cho file đang được upload
    const uploadingIndicator = showUploadingIndicator(file.name);

    const formData = new FormData();
    formData.append('file', file);
    // Gửi sessionId dưới key "collection"
    formData.append('collection', sessionId);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload_file', true);
    xhr.onload = () => {
        if (uploadingIndicator && uploadingIndicator.parentNode) {
            uploadingIndicator.parentNode.removeChild(uploadingIndicator);
        }
        if (xhr.status === 200) {
            showSuccessMessage('File uploaded successfully.');
            appendUploadedFile(file);
        } else {
            showFileErrorMessage('Error uploading file: ' + xhr.statusText);
        }
    };
    xhr.onerror = () => {
        if (uploadingIndicator && uploadingIndicator.parentNode) {
            uploadingIndicator.parentNode.removeChild(uploadingIndicator);
        }
        showFileErrorMessage('Network error occurred while uploading file');
    };
    xhr.send(formData);
}

// Gửi câu hỏi đến server khi click nút "Send" hoặc nhấn Enter (gửi kèm sessionId)
sendQuestionButton.addEventListener('click', () => {
    const question = chatInput.value.trim();
    if (question) {
        sendQuestion(question);
        chatInput.value = '';
    }
});

chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        const question = chatInput.value.trim();
        if (question) {
            sendQuestion(question);
            chatInput.value = '';
        }
    }
});

function sendQuestion(question) {
    displayMessage('You: ' + question, 'user-message');
    displayTypingIndicator();
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/ask_question', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = () => {
        removeTypingIndicator();
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            // Giả sử phản hồi từ server là Markdown
            displayMarkdownMessage('Assistant: ' + response.response, 'assistant-message');
        } else {
            displayMessage('Error: ' + xhr.statusText, 'error-message');
        }
    };
    xhr.onerror = () => {
        removeTypingIndicator();
        displayMessage('Network error occurred while sending question', 'error-message');
    };
    // Gửi JSON chứa câu hỏi và sessionId (dưới key "collection")
    xhr.send(JSON.stringify({ question: question, collection: sessionId }));
}
// Xử lý nút "Summarize" (gửi sessionId qua query param)
summarizeButton.addEventListener('click', () => {
    sendSummarize();
});

function sendSummarize() {
    displayMessage('Requesting summary...', 'system-message');
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/summarize', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = () => {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            // Giả sử phản hồi từ server là Markdown
            displayMarkdownMessage(response.response, 'assistant-message');
        } else {
            displayMessage('Error summarizing: ' + xhr.statusText, 'error-message');
        }
    };
    xhr.onerror = () => {
        displayMessage('Network error occurred while summarizing', 'error-message');
    };
    // Gửi JSON chứa sessionId (dưới key "collection")
    xhr.send(JSON.stringify({ collection: sessionId }));
}

function createThread() {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/create_thread', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = () => {
        if (xhr.status === 200) {
            showSuccessMessage('Thread created successfully.');
        } else {
            showErrorMessage('Error creating thread: ' + xhr.statusText);
        }
    };
    xhr.onerror = () => {
        showErrorMessage('Network error occurred while creating thread');
    };
    xhr.send(JSON.stringify({ collection: sessionId }));
}

createThread();
