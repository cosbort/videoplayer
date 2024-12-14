import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os
from tkinter import messagebox
from moviepy.editor import VideoFileClip
import threading
import time
import pygame

class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")
        self.root.geometry("800x600")
        
        # Inizializzazione pygame per l'audio
        pygame.init()
        pygame.mixer.init()
        
        # Variabili di stato
        self.video_clip = None
        self.current_frame = None
        self.is_playing = False
        self.current_time = 0
        self.speed = 1.0
        self.frame_interval = 1/30  # 30 FPS di default
        
        # Stile
        style = ttk.Style()
        style.configure("Custom.TButton", padding=5, font=('Helvetica', 10))
        
        # Frame principale
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(expand=True, fill='both')
        
        # Area video
        self.video_frame = ttk.Frame(self.main_frame, relief='solid', borderwidth=1)
        self.video_frame.pack(expand=True, fill='both', pady=5)
        
        # Label per il video
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(expand=True, fill='both')
        self.video_label.configure(text="Nessun video selezionato\nClicca 'Apri Video' per iniziare")
        
        # Frame per i controlli
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill='x', pady=5)
        
        # Controlli
        ttk.Button(control_frame, text="Apri Video", style="Custom.TButton", 
                  command=self.open_video).pack(side='left', padx=5)
        ttk.Button(control_frame, text="⏪⏪", style="Custom.TButton", 
                  command=lambda: self.change_speed(-2)).pack(side='left', padx=5)
        ttk.Button(control_frame, text="⏪", style="Custom.TButton", 
                  command=lambda: self.change_speed(-1)).pack(side='left', padx=5)
        self.play_button = ttk.Button(control_frame, text="▶", style="Custom.TButton", 
                                    command=self.toggle_play)
        self.play_button.pack(side='left', padx=5)
        ttk.Button(control_frame, text="⏩", style="Custom.TButton", 
                  command=lambda: self.change_speed(1)).pack(side='left', padx=5)
        ttk.Button(control_frame, text="⏩⏩", style="Custom.TButton", 
                  command=lambda: self.change_speed(2)).pack(side='left', padx=5)
        
        # Progress bar
        self.progress = ttk.Scale(self.main_frame, orient="horizontal", from_=0, to=100,
                                command=self.seek)
        self.progress.pack(fill='x', pady=5)
        
        # Etichetta tempo
        self.time_label = ttk.Label(self.main_frame, text="00:00 / 00:00")
        self.time_label.pack(pady=5)
        
        # Thread per l'aggiornamento del frame
        self.update_thread = None
        self.stop_thread = False

    def open_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mkv")]
        )
        if file_path:
            try:
                if self.video_clip is not None:
                    self.video_clip.close()
                
                self.video_clip = VideoFileClip(file_path)
                self.frame_interval = 1.0 / self.video_clip.fps
                self.current_time = 0
                self.update_time_label()
                self.toggle_play()
                
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile aprire il video: {str(e)}")

    def toggle_play(self):
        if self.video_clip:
            self.is_playing = not self.is_playing
            self.play_button.config(text="⏸" if self.is_playing else "▶")
            
            if self.is_playing:
                if self.update_thread is None or not self.update_thread.is_alive():
                    self.stop_thread = False
                    self.update_thread = threading.Thread(target=self.update_frame, daemon=True)
                    self.update_thread.start()
            else:
                self.stop_thread = True

    def update_frame(self):
        while not self.stop_thread and self.video_clip:
            try:
                # Ottieni il frame corrente
                frame = self.video_clip.get_frame(self.current_time)
                
                # Converti il frame in un'immagine Tkinter
                image = Image.fromarray(frame)
                # Ridimensiona l'immagine per adattarla alla finestra
                image = image.resize((640, 360), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Aggiorna l'immagine
                self.video_label.configure(image=photo)
                self.video_label.image = photo
                
                # Aggiorna il tempo e la barra di progresso
                self.current_time += self.frame_interval * self.speed
                if self.current_time >= self.video_clip.duration:
                    self.current_time = 0
                    self.is_playing = False
                    self.play_button.config(text="▶")
                    break
                
                self.update_time_label()
                self.progress.set((self.current_time / self.video_clip.duration) * 100)
                
                # Attendi il prossimo frame
                time.sleep(self.frame_interval / abs(self.speed))
                
            except Exception as e:
                print(f"Errore durante l'aggiornamento del frame: {str(e)}")
                break

    def change_speed(self, speed):
        if self.video_clip:
            speeds = {-2: 0.5, -1: 0.75, 1: 1.5, 2: 2.0}
            self.speed = speeds[speed]
            messagebox.showinfo("Velocità", f"Velocità impostata a: {self.speed}x")

    def seek(self, value):
        if self.video_clip:
            self.current_time = (float(value) / 100.0) * self.video_clip.duration
            self.update_time_label()

    def update_time_label(self):
        if self.video_clip:
            current = int(self.current_time)
            total = int(self.video_clip.duration)
            self.time_label.config(text=f"{self._format_time(current)} / {self._format_time(total)}")

    def _format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def __del__(self):
        if self.video_clip:
            self.video_clip.close()
        pygame.quit()

if __name__ == "__main__":
    root = tk.Tk()
    player = VideoPlayer(root)
    root.mainloop()
