const BASE_URL = "http://127.0.0.1:5000";

// ---------------- TOKEN HANDLING ----------------

function saveToken(token) {
    localStorage.setItem("token", token);
}

function getToken() {
    return localStorage.getItem("token");
}

function logout() {
    localStorage.removeItem("token");
    location.reload();
}

// ---------------- UI CONTROL ----------------

function showApp() {
    document.getElementById("authSection").style.display = "none";
    document.getElementById("appSection").style.display = "block";
}

// ---------------- AUTH ----------------

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
    .then(data => {
        document.getElementById("message").innerText = data.message;
    });
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
    .then(data => {
        document.getElementById("message").innerText = data.message;

        if (data.token) {
            saveToken(data.token);
            showApp();
            loadFiles(); // load dashboard
        }
    });
}

// ---------------- FILE UPLOAD ----------------

function uploadFile() {
    const token = getToken();

    if (!token) {
        document.getElementById("message").innerText = "Please login first";
        return;
    }

    const fileInput = document.getElementById("fileInput");

    if (fileInput.files.length === 0) {
        document.getElementById("message").innerText = "Select a file";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch(BASE_URL + "/upload", {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("message").innerText = data.message;

        if (data.download_link) {
            document.getElementById("linkDisplay").innerText =
                "Download Link: " + data.download_link;
        }

        loadFiles(); // refresh dashboard
    });
}

// ---------------- LOAD DASHBOARD ----------------

function loadFiles() {
    const token = getToken();

    fetch(BASE_URL + "/myfiles", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        const table = document.getElementById("fileTable");
        table.innerHTML = "";

        data.forEach(file => {
            const row = `
                <tr>
                    <td>${file.filename}</td>
                    <td>${file.expiry}</td>
                    <td>
                        <button onclick="downloadById('${file.file_id}')">
                            Download
                        </button>
                    </td>
                </tr>
            `;
            table.innerHTML += row;
        });
    });
}

// ---------------- DOWNLOAD BY FILE ID ----------------

function downloadFile() {
    const token = getToken();
    const fileId = document.getElementById("fileIdInput").value;

    if (!token) {
        document.getElementById("message").innerText = "Please login first";
        return;
    }

    if (!fileId) {
        document.getElementById("message").innerText = "Enter file ID";
        return;
    }

    downloadById(fileId);
}

// ---------------- DOWNLOAD HELPER ----------------

function downloadById(fileId) {
    const token = getToken();

    fetch(BASE_URL + "/download/" + fileId, {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Download failed (maybe expired or unauthorized)");
        }
        return res.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "file";
        a.click();
    })
    .catch(err => {
        document.getElementById("message").innerText = err.message;
    });
}

// ---------------- AUTO LOGIN ----------------

window.onload = function() {
    if (getToken()) {
        showApp();
        loadFiles();
    }
};