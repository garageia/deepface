import base64
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template
from deepface import DeepFace

app = Flask(__name__)

# Chargement du modèle pour la détection de visages en utilisant Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Chargement du dataset de photos
dataset = {
    "Aziz": "image/aziz.jpg",
    "Silue": "image/silue.jpeg",
}

# Route pour afficher la page d'accueil
@app.route('/')
def home():
    return render_template('index1.html')

# Route pour la détection de visages à partir de l'image envoyée par le client
@app.route('/visage', methods=['POST'])
def visage():
    # Récupération de l'image encodée en base64 depuis le client
    image_data = request.form['image'].split(",")[1]
    img = base64.b64decode(image_data)
    nparr = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Détection des visages en utilisant le modèle Haar Cascade
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    data = []
    for (x, y, w, h) in faces:
        # Récupération de l'image du visage
        face_img = img[y:y+h, x:x+w]
        
        # Utilisation de DeepFace pour obtenir le genre et l'émotion
        demography = DeepFace.analyze(img_path=face_img, enforce_detection=False, actions=['gender', 'emotion', 'race', 'age'])
        gender = demography[0]['dominant_gender']
        emotion = demography[0]['dominant_emotion']
        race = demography[0]['dominant_race']
        age = demography[0]['age']
        
        # Recherche du nom correspondant au visage en utilisant le dataset de photos
        face_name = "Inconnu"
        for name, img_path in dataset.items():
            img2 = cv2.imread(img_path)
            result = cv2.matchTemplate(face_img, img2, cv2.TM_CCOEFF_NORMED)
            similarity = result[0][0]
            if similarity > 0.2:
                face_name = name
                break
        
        # Ajout des informations sur le visage à la liste de données
        data.append({
            'gender': str(gender),
            'emotion': str(emotion),
            'race': str(race),
            'age': int(age),
            'name': str(face_name)
        }) 
    
    # Renvoyer les informations au client
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
