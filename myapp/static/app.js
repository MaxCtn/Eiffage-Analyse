document.getElementById("analyze").addEventListener("click", function () {
    var membersFileInput = document.getElementById("membersFile");
    var invoicesFileInput = document.getElementById("invoicesFile");

    var formData = new FormData();
    formData.append("file", membersFileInput.files[0]);
    formData.append("file", invoicesFileInput.files[0]);

    var request = new XMLHttpRequest();
    request.open("POST", "/analyze");

    request.onload = function () {
        if (request.status === 200) {
            var response = JSON.parse(request.responseText);
            var downloadButton = document.getElementById("download");
            downloadButton.style.display = "block";

            downloadButton.onclick = function () {
                var file_paths = response.result_file_path.join(",");

                window.location.href = "/download?file_paths=" + encodeURIComponent(file_paths);
            };
        } else {
            console.error("Erreur lors de l'analyse des fichiers. Statut:", request.status, "Réponse:", request.responseText);

        }
    };

    request.send(formData);
});

// Gérer les boutons supprimer pour retirer les fichiers des inputs
document.getElementById("removeMembers").addEventListener("click", function () {
    var membersFileInput = document.getElementById("membersFile");
    membersFileInput.value = "";
    document.querySelector(".input-image.members").style.backgroundImage = `url("https://cdn.discordapp.com/attachments/1097452094685986899/1097498221665853560/ajouter-le-fichier1.png")`;
    document.getElementById("membersFileName").textContent = "";
});

document.getElementById("removeInvoices").addEventListener("click", function () {
    var invoicesFileInput = document.getElementById("invoicesFile");
    invoicesFileInput.value = "";
    document.querySelector(".input-image.invoices").style.backgroundImage = `url("https://cdn.discordapp.com/attachments/1097452094685986899/1097498221665853560/ajouter-le-fichier1.png")`;
    document.getElementById("invoicesFileName").textContent = "";
});

document.querySelector('.input-image.members').addEventListener('click', function () {
    document.querySelector('#membersFile').click();
});

document.querySelector('.input-image.invoices').addEventListener('click', function () {
    document.querySelector('#invoicesFile').click();
});

function handleFileInputChange(event, imageSelector) {
    const fileInput = event.target;
    const imageElement = document.querySelector(imageSelector);
    const fileNameElementId = fileInput.id === "membersFile" ? "membersFileName" : "invoicesFileName";
    const fileNameElement = document.getElementById(fileNameElementId);

    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            imageElement.style.backgroundImage = `url("https://cdn.discordapp.com/attachments/1097452094685986899/1097498222596988988/valide.png")`;
        }

        reader.readAsDataURL(fileInput.files[0]);
        fileNameElement.textContent = fileInput.files[0].name;
    } else {
        imageElement.style.backgroundImage = `url("https://cdn.discordapp.com/attachments/1097452094685986899/1097498221665853560/ajouter-le-fichier1.png")`;
        fileNameElement.textContent = "";
    }
}

document.getElementById("membersFile").addEventListener("change", (event) => {
    handleFileInputChange(event, ".input-image.members");
});

document.getElementById("invoicesFile").addEventListener("change", (event) => {
    handleFileInputChange(event, ".input-image.invoices");
});
