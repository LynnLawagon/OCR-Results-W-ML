const droparea = document.getElementById("drop-area");
const inputfile = document.getElementById("input-file");
const previewImg = document.getElementById("preview-img");
const resultText = document.getElementById("result-text");
const loadingIndicator = document.getElementById("loading-indicator");

function uploadImage(file) {
    if (!file) return;
    const imgLink = URL.createObjectURL(file);
    previewImg.src = imgLink;

    // Show loading
    loadingIndicator.style.display = "block";
    resultText.textContent = ""; 

    // Send to Flask
    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let output = "";
        for (const key in data) {
            output += `${key}: ${data[key]}\n`;
        }
        resultText.textContent = output;
    })
    .catch(err => {
        console.error(err);
        resultText.textContent = "Error processing image";
    })
    .finally(() => {
        loadingIndicator.style.display = "none";
    });
}

// File select
inputfile.addEventListener("change", () => uploadImage(inputfile.files[0]));

// Drag & drop
droparea.addEventListener("dragover", (event) => {
    event.preventDefault();
    droparea.classList.add("dragover");
});

droparea.addEventListener("dragleave", () => {
    droparea.classList.remove("dragover");
});

droparea.addEventListener("drop", (event) => {
    event.preventDefault();
    droparea.classList.remove("dragover");
    const file = event.dataTransfer.files[0];
    uploadImage(file);
});
