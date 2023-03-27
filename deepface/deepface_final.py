import base64
from flask import Flask, request, jsonify, render_template, Response
import cv2
from deepface import DeepFace
import numpy as np
app = Flask(__name__)

# Chargement du modèle pour la détection de visages en utilisant Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Chargement du dataset de photos
dataset = {
    "Aziz": "E:\Toure\exo python\photo\AZIZ.jpg",
    "Voisin": "E:\Toure\exo python\photo\presi.jpg",
    "Presi": "E:\Toure\exo python\photo\photo.jpg"
}

# Route pour afficher la page d'accueil
@app.route('/')
def home():
    return render_template('commun.html')
@app.route('/index')
def index():
    return render_template('index.html')
# Route pour la détection de visages à partir d'une image téléchargée
@app.route('/visage', methods=['POST'])
def visage():
    # Récupération de l'image téléchargée
    file = request.files['image']
    img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    
    # Détection des visages en utilisant le modèle Haar Cascade
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    # Pour chaque visage détecté, attribuer un nom à partir du dataset et afficher le genre et l'émotion en utilisant DeepFace
    data = []
    for (x, y, w, h) in faces:
        # Récupération de l'image du visage
        face_img = img[y:y+h, x:x+w]
        _, buffer = cv2.imencode('.jpg', face_img)
    
    # Encodage de la matrice d'images en base64
        face_bytes = base64.b64encode(buffer).decode('utf-8')
        
        # Utilisation de DeepFace pour obtenir le genre et l'émotion
        demography = DeepFace.analyze(img_path=face_img,enforce_detection=False, actions=['gender', 'emotion','race','age'])
        gender = demography[0]['dominant_gender']
        emotion = demography[0]['dominant_emotion']
        race = demography[0]['dominant_race']
        age=demography[0]['age']
        
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
        'image': face_bytes,
        
        'gender': str(gender),
        'emotion': str(emotion),
        'race': str(race),
        'age': int(age),
        'name': str(face_name)
    }) 
        
    
    # Conversion des données en format JSON et envoi de la réponse
    return render_template('result.html', data=data)
# Route pour la détection de visages à partir d'une image téléchargée


def gen():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
        
            # Utilisation de DeepFace pour obtenir le genre et l'émotion
            demography = DeepFace.analyze(img_path=face_img,enforce_detection=False, actions=['gender', 'emotion','race','age'])
            gender = demography[0]['dominant_gender']
            emotion = demography[0]['dominant_emotion']
            race = demography[0]['dominant_race']
            age=demography[0]['age']
            face_name = "Inconnu"
            for name, img_path in dataset.items():
                img = cv2.imread(img_path)
                result = cv2.matchTemplate(face_img, img, cv2.TM_CCOEFF_NORMED)
                similarity = result[0][0]
                if similarity > 0.5:
                    face_name = name
                    break
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Emotion: {emotion}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(frame, f"Gender: {gender}", (0, y+h+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, f"Nom: {face_name}", (x, y+h+60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(frame, f"Race: {race}", (0, y+h+80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(frame, f"Age: {age}", (x, y+h+90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        frame = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/detect')
def detect():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
