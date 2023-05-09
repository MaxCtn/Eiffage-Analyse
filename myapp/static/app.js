function handleFileInputChange(event, imageSelector) {
    const fileInput = event.target;
    const imageElement = document.querySelector(imageSelector);
    const fileNameElementId =
        fileInput.id === "membersFile" ? "membersFileName" : "invoicesFileName";
    const fileNameElement = document.getElementById(fileNameElementId);

    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            imageElement.style.backgroundImage = `url("https://cdn.discordapp.com/attachments/1097452094685986899/1097498222596988988/valide.png")`;
        };

        reader.readAsDataURL(fileInput.files[0]);
        fileNameElement.textContent = fileInput.files[0].name;
    } else {
        imageElement.style.backgroundImage = `url("https://cdn.discordapp.com/attachments/1097452094685986899/1097498221665853560/ajouter-le-fichier1.png")`;
        fileNameElement.textContent = "";
    }
}

function updateDownloadLink(result_file_path) {
    const downloadLink = document.getElementById("download-link");
    downloadLink.href = `/download?result_file_path=${encodeURIComponent(result_file_path)}`;
    downloadLink.style.display = "block";
}


document.getElementById("analyze").addEventListener("click", function () {
    const membersFile = document.getElementById("membersFile").files[0];
    const invoicesFile = document.getElementById("invoicesFile").files[0];

    if (!membersFile || !invoicesFile) {
        alert("Veuillez sélectionner les fichiers Membres et Factures.");
        return;
    }

    const formData = new FormData();
    formData.append("membersFile", membersFile);
    formData.append("invoicesFile", invoicesFile);

    const loadingIndicator = document.getElementById("loadingIndicator");
    loadingIndicator.style.display = "block";

    fetch("/analyze", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.text()) // Changez ceci pour traiter la réponse en tant que texte
        .then((data) => {
            loadingIndicator.style.display = "none";

            if (data) {
                updateDownloadLink(data);
            }
        })
        .catch((error) => {
            loadingIndicator.style.display = "none";
            console.error("Error:", error);
        });

});

