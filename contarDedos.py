import cv2
import mediapipe as mp
import os
import csv

# Inicializa MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)

# Cria pasta de saída para os dados
os.makedirs("dados_csv", exist_ok=True)

# Abre CSV para escrever os dados
csv_file = open("dados_csv/letras.csv", 'w', newline='', encoding='utf-8')
writer = csv.writer(csv_file)
writer.writerow([f"x{i}" for i in range(21)] + [f"y{i}" for i in range(21)] + ["letra"])

# Pasta dos vídeos
video_dir = "videos"

# Processar todos os vídeos
for video_file in os.listdir(video_dir):
    if video_file.endswith(".mp4"):
        letra = video_file[0].upper()  # Primeira letra do nome
        caminho_video = os.path.join(video_dir, video_file)
        print(f"Processando {video_file} como letra {letra}")

        cap = cv2.VideoCapture(caminho_video)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultado = hands.process(rgb)

            if resultado.multi_hand_landmarks:
                for hand_landmarks in resultado.multi_hand_landmarks:
                    x = [lm.x for lm in hand_landmarks.landmark]
                    y = [lm.y for lm in hand_landmarks.landmark]
                    writer.writerow(x + y + [letra])
                    break  # Um frame por gesto

        cap.release()

csv_file.close()
print("✅ Processamento finalizado e dados salvos em 'dados_csv/letras.csv'")