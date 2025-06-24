import tkinter as tk
from tkinter import ttk
import cv2
import mediapipe as mp
import joblib
import numpy as np
import threading
import queue
from PIL import Image, ImageTk
import pyttsx3
from playsound import playsound
import os
import time

# Configurações
video_dir = "videos"
som_acerto = "acerto.mp3"
letras = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
modelo = joblib.load("modelo_letras_knn.pkl")

# MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)

# Áudio
voz = pyttsx3.init()
voz.setProperty('rate', 150)
voz_queue = queue.Queue()

def voz_worker():
    while True:
        frase = voz_queue.get()
        if frase is None:
            break
        voz.say(frase)
        voz.runAndWait()

threading.Thread(target=voz_worker, daemon=True).start()

def falar_letra(texto):
    voz_queue.put(texto)

def tocar_acerto():
    threading.Thread(target=lambda: playsound(som_acerto), daemon=True).start()

def prever_letra(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            x = [lm.x for lm in hand_landmarks.landmark]
            y = [lm.y for lm in hand_landmarks.landmark]
            dados = np.array(x + y).reshape(1, -1)
            return modelo.predict(dados)[0]
    return None

# Interface Principal
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aprendizado Interativo por Gestos")
        self.root.configure(bg="#fdf6f0")
        self.current_index = 0
        self.acertou = False
        self.predicao = None
        self.last_inference_time = 0
        self.inference_interval = 0.1

        self.label_letra = tk.Label(root, text="", font=("Comic Sans MS", 42, "bold"),
                                    fg="#007acc", bg="#fdf6f0")
        self.label_letra.pack(pady=10)

        self.progress = ttk.Progressbar(root, maximum=len(letras))
        self.progress.pack(fill='x', padx=15, pady=5)

        self.canvas = tk.Canvas(root, width=640, height=240, bg="#ffffff", highlightthickness=1)
        self.canvas.pack(pady=10)

        self.btn_sair = ttk.Button(root, text="Sair", command=self.sair)
        self.btn_sair.pack(pady=10)

        self.webcam = cv2.VideoCapture(0)
        self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.video = None

        self.atualizar_letra()
        self.update_frame()

    def atualizar_letra(self):
        letra = letras[self.current_index]
        self.label_letra.config(text=f"Letra: {letra}")
        self.progress['value'] = self.current_index + 1

        if self.video is not None:
            self.video.release()
        video_nome = f"{letra.lower()}Sm_Prog001.mp4"
        video_path = os.path.join(video_dir, video_nome)
        self.video = cv2.VideoCapture(video_path)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        falar_letra(f"Letra {letra}")
        self.acertou = False

    def update_frame(self):
        ret_vid, frame_vid = self.video.read()
        if not ret_vid:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_vid, frame_vid = self.video.read()

        ret_cam, frame_cam = self.webcam.read()
        if not ret_cam:
            self.root.after(100, self.update_frame)
            return

        frame_cam = cv2.flip(frame_cam, 1)
        frame_cam = cv2.resize(frame_cam, (320, 240))
        frame_vid = cv2.resize(frame_vid, (320, 240))

        rgb_cam = cv2.cvtColor(frame_cam, cv2.COLOR_BGR2RGB)
        resultado = hands.process(rgb_cam)
        if resultado.multi_hand_landmarks:
            for hand_landmarks in resultado.multi_hand_landmarks:
                 mp_drawing.draw_landmarks(
                    frame_cam, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=4, circle_radius=2),  # Pontos: amarelo neon
                    mp_drawing.DrawingSpec(color=(255, 20, 147), thickness=3)                  # Linhas: rosa neon
        )

        current_time = time.time()
        if current_time - self.last_inference_time >= self.inference_interval:
            self.last_inference_time = current_time
            self.predicao = prever_letra(frame_cam)

        letra = letras[self.current_index]
        cv2.putText(frame_cam, f"Letra: {letra}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        if self.predicao == letra and not self.acertou:
            cv2.putText(frame_cam, "Correto!", (60, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 200, 0), 4)
            tocar_acerto()
            self.acertou = True
            self.root.after(2500, self.proximo)

        combinado = cv2.hconcat([frame_cam, frame_vid])
        img_rgb = cv2.cvtColor(combinado, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
        self.canvas.img_tk = img_tk

        self.root.after(100, self.update_frame)

    def proximo(self):
        if self.current_index + 1 < len(letras):
            self.current_index += 1
            self.atualizar_letra()
        else:
            falar_letra("Fim do alfabeto! Parabéns!")
            self.sair()

    def sair(self):
        self.webcam.release()
        if self.video is not None:
            self.video.release()
        self.root.destroy()

# Tela Inicial
class TelaInicial:
    def __init__(self, root):
        self.root = root
        self.root.title("Bem-vindo!")
        self.root.geometry("500x300")
        self.root.configure(bg="#e6f7ff")

        titulo = tk.Label(root, text="Aprendizado Interativo por Gestos", 
                          font=("Comic Sans MS", 20, "bold"), 
                          fg="#007acc", bg="#e6f7ff", pady=20)
        titulo.pack()

        iniciar = ttk.Button(root, text="Iniciar", command=self.abrir_app)
        iniciar.pack(pady=50, ipadx=20, ipady=10)

    def abrir_app(self):
        self.root.destroy()
        nova_janela = tk.Tk()
        App(nova_janela)
        nova_janela.mainloop()

# Início da aplicação
if __name__ == "__main__":
    tela = tk.Tk()
    TelaInicial(tela)
    tela.mainloop()