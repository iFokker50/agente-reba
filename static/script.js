const imageInput = document.getElementById("imageInput");
const uploadText = document.getElementById("uploadText");
const previewContainer = document.getElementById("previewContainer");
const previewImage = document.getElementById("previewImage");
const analyzeButton = document.getElementById("analyzeButton");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");
const resultCard = document.getElementById("resultCard");
const reportOutput = document.getElementById("reportOutput");
const copyButton = document.getElementById("copyButton");

let selectedFile = null;
let lastReport = "";

imageInput.addEventListener("change", function () {
    selectedFile = imageInput.files[0];

    errorBox.classList.add("hidden");
    resultCard.classList.add("hidden");

    if (!selectedFile) {
        return;
    }

    uploadText.textContent = selectedFile.name;

    const reader = new FileReader();

    reader.onload = function (e) {
        previewImage.src = e.target.result;
        previewContainer.style.display = "block";
    };

    reader.readAsDataURL(selectedFile);
});

analyzeButton.addEventListener("click", async function () {
    if (!selectedFile) {
        showError("Primero selecciona una imagen.");
        return;
    }

    const selectedSide = document.querySelector("input[name='bodySide']:checked").value;

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("body_side", selectedSide);

    loading.classList.remove("hidden");
    errorBox.classList.add("hidden");
    resultCard.classList.add("hidden");
    analyzeButton.disabled = true;

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!data.success) {
            showError(data.message || "Ocurrió un error al analizar la imagen.");
            return;
        }

        lastReport = data.report;

        reportOutput.innerHTML = marked.parse(data.report);
        resultCard.classList.remove("hidden");

        resultCard.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {
        showError("Error de conexión con el backend.");
    } finally {
        loading.classList.add("hidden");
        analyzeButton.disabled = false;
    }
});

copyButton.addEventListener("click", async function () {
    if (!lastReport) {
        return;
    }

    await navigator.clipboard.writeText(lastReport);

    copyButton.textContent = "Copiado";
    setTimeout(() => {
        copyButton.textContent = "Copiar reporte";
    }, 1500);
});

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}