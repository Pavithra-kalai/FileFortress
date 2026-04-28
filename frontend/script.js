const BASE_URL = "http://127.0.0.1:5000";

// Register
function register() {
    const username = document.getElementById("reg_username").value;
    const password = document.getElementById("reg_password").value;

    fetch(BASE_URL + "/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => document.getElementById("message").innerText = data.message);
}

// Login
function login() {
    const username = document.getElementById("login_username").value;
    const password = document.getElementById("login_password").value;

    fetch(BASE_URL + "/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => document.getElementById("message").innerText = data.message);
}

// Upload File
function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch(BASE_URL + "/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => document.getElementById("message").innerText = data.message);
}