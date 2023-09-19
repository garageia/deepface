document.addEventListener("DOMContentLoaded", () => {
            const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");

    // Ouvrir la webcam et afficher le flux vidéo
    navigator.mediaDevices.getUserMedia({video: true })
                .then((stream) => {
        video.srcObject = stream;
                })
                .catch((error) => {
        console.error("Erreur lors de l'accès à la webcam:", error);
                });

    // Capture du flux vidéo et envoi des images au serveur Flask pour traitement
    function processWebcamStream() {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL("image/jpeg", 0.8);

    fetch("/visage", {
        method: "POST",
    body: new URLSearchParams({
        image: imageData
                    }),
    headers: {
        "Content-Type": "application/x-www-form-urlencoded"
                    }
                })
                .then((response) => response.json())
                .then((data) => {
                    // Traiter les informations reçues du serveur Flask
                    if (data.length > 0) {
                        const faceData = data[0];
    document.getElementById("genre").textContent = faceData.gender;
    document.getElementById("emotion").textContent = faceData.emotion;
    document.getElementById("age").textContent = faceData.age;
                    }
                })
                .catch((error) => {
        console.error("Erreur lors de l'envoi des données au serveur:", error);
                });

    // Répéter la capture toutes les X millisecondes (par exemple toutes les 500ms)
    setTimeout(processWebcamStream, 500);
            }

    // Démarrer le traitement du flux vidéo
    processWebcamStream();
        });
