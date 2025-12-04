const CLIENT_ID = '230207934679-rljtq2o0vh7kkdemeo9qkgt1v9osl33k.apps.googleusercontent.com'; 

// --- Google Auth & UI Logic ---
function handleCredentialResponse(response) {
    const decoded = JSON.parse(atob(response.credential.split('.')[1]));
    const email = decoded.email;
    const name = decoded.name || email;
    const picture = decoded.picture || "";

    CURRENT_USER = email;

    document.getElementById('userName').innerText = name;
    document.getElementById('userImg').src = picture;
    document.getElementById('userProfile').style.display = 'flex';
    document.getElementById('signinArea').style.display = 'none';

    loadChatHistory();
}

function logout() {
    CURRENT_USER = null;
    document.getElementById('userName').innerText = '';
    document.getElementById('userImg').src = '';
    document.getElementById('userProfile').style.display = 'none';
    document.getElementById('signinArea').style.display = 'block';
    document.getElementById("chatHistoryList").innerHTML = "";
    document.getElementById("chatHistorySection").style.display = "none";
}

window.onload = function() {
    google.accounts.id.initialize({
        client_id : CLIENT_ID,
        callback: handleCredentialResponse
    });
    google.accounts.id.renderButton(
        document.getElementById('g_id_signin'),
        { theme: 'outline', size: 'large', text: 'signin_with', shape: 'pill' }
    );
};

const sidebar = document.getElementById('sidebar');
const main = document.getElementById('mainContent');
const openBtn = document.getElementById('openSidebar');
const closeBtn = document.getElementById('closeSidebar');

openBtn.addEventListener('click', () => {
    sidebar.classList.remove('closed');
    main.classList.remove('full');
    openBtn.style.display = 'none';
});

closeBtn.addEventListener('click', () => {
    sidebar.classList.add('closed');
    main.classList.add('full');
    openBtn.style.display = 'block';
});

let CURRENT_USER = null;

// --- History Logic ---
function loadChatHistory() {
    if (!CURRENT_USER) return;
    const key = "chatHistory_" + CURRENT_USER;
    const history = JSON.parse(localStorage.getItem(key)) || [];
    const list = document.getElementById("chatHistoryList");
    list.innerHTML = "";
    history.forEach((item, index) => {
        const li = document.createElement("li");
        li.className = "history-item";
        li.innerText = item.question.substring(0, 40) + "...";
        li.onclick = () => loadChatFromHistory(index);
        list.appendChild(li);
    });
    document.getElementById("chatHistorySection").style.display = "block";
}

function saveChat(question, answer) {
    if (!CURRENT_USER) return;
    const key = "chatHistory_" + CURRENT_USER;
    const history = JSON.parse(localStorage.getItem(key)) || [];
    history.push({ question, answer });
    localStorage.setItem(key, JSON.stringify(history));
    loadChatHistory();
}

function loadChatFromHistory(index) {
    const key = "chatHistory_" + CURRENT_USER;
    const history = JSON.parse(localStorage.getItem(key)) || [];
    const chat = history[index];
    document.getElementById("userInput").value = chat.question;
    document.getElementById("response").innerHTML = marked.parse(chat.answer);
}

function deleteChatHistory() {
    if (!CURRENT_USER) return;
    if (!confirm("Are you sure you want to delete all chat history?")) return;
    localStorage.removeItem("chatHistory_" + CURRENT_USER);
    document.getElementById("chatHistoryList").innerHTML = "";
    document.getElementById("chatHistorySection").style.display = "none";
    document.getElementById("response").innerHTML = "Chat history cleared.";
}

// --- NEW Backend Connection Logic ---
async function sendMessage() {
    const input = document.getElementById('userInput').value;
    const responseDiv = document.getElementById('response');

    if (!input) {
        responseDiv.innerHTML = 'Please enter a message.';
        return;
    }
    if(!CURRENT_USER){ 
        responseDiv.innerHTML = 'Please sign in to use the bot.';
        return;
    }

    responseDiv.innerHTML = 'Thinking...';

    try {
        // We now fetch from our OWN Python Backend, not Groq directly
        const response = await fetch('https://the-searchbot-3.onrender.com/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        const markdownText = data.reply;
        responseDiv.innerHTML = marked.parse(markdownText);
        saveChat(input, markdownText);

    } catch (error) {
        responseDiv.innerHTML = 'Error: ' + error.message;
        console.error(error);
    }
}
