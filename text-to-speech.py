import tkinter as tk
from tkinter import messagebox, filedialog
from openai import OpenAI
import pygame
import tempfile

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text-to-speech")
        self.geometry("600x380")
        self.configure(bg='#333333')
        
        pygame.mixer.init()
        
        # input text
        self.text_field = tk.Text(self, height=16, width=80, bg="#4F4F4F", fg="white", insertbackground='white')
        self.text_field.pack(padx=10, pady=10)
        
        # button frame
        self.button_frame = tk.Frame(self, bg='#333333')
        self.button_frame.pack(padx=10, pady=5, anchor='w')

        # Voice selection dropdown menu
        self.selected_voice = tk.StringVar(self)
        self.selected_voice.set("alloy")
        self.voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.voice_dropdown = tk.OptionMenu(self.button_frame, self.selected_voice, *self.voice_options)
        self.voice_dropdown.config(bg="#555555", fg="white")
        self.voice_dropdown.pack(side=tk.LEFT, padx=(0, 10))

        # play button
        self.tts_btn = tk.Button(self.button_frame, text="Play", command=self.generate_and_play_audio, bg="#555555", fg="white")
        self.tts_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # pause button
        self.pause_btn = tk.Button(self.button_frame, text="Pause", command=self.pause_audio, bg="#555555", fg="white")
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # stop button
        self.stop_btn = tk.Button(self.button_frame, text="Stop", command=self.stop_audio, bg="#555555", fg="white")
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        # download button
        self.download_btn = tk.Button(self.button_frame, text="⬇️Download", command=self.download_audio, bg="#555555", fg="white", state='disabled')
        self.download_btn.pack(side=tk.LEFT)

        # openai api key
        self.api_key_label = tk.Label(self, text="OpenAI API key:", bg='#333333', fg="white")
        self.api_key_label.pack(padx=10, pady=5, anchor='w')
        
        self.api_key_entry = tk.Entry(self, width=60, bg="#4F4F4F", fg="white", insertbackground='white')
        self.api_key_entry.pack(padx=10, anchor='w')
        
        self.audio_file_path = None
        self.is_paused = False

    def generate_and_play_audio(self):
        voice = self.selected_voice.get()
        if self.is_paused:
            self.play_audio()
        else:
            text = self.text_field.get(1.0, "end-1c")
            api_key = self.api_key_entry.get()
            if not api_key:
                messagebox.showerror("Error", "Please enter a valid OpenAI API key!")
                return

            client = OpenAI(api_key=api_key)

            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                )
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                    tmp.write(response.content)
                    self.audio_file_path = tmp.name
                
                self.download_btn['state'] = 'normal'
                self.play_audio()

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred reading the text: {e}")

    def download_audio(self):
        if self.audio_file_path:
            default_name = "tts_audio.mp3"
            file_path = filedialog.asksaveasfilename(defaultextension=".mp3", initialfile=default_name, filetypes=[(".mp3", "*.mp3")])
            if file_path:
                with open(self.audio_file_path, 'rb') as source_file:
                    with open(file_path, 'wb') as dest_file:
                        dest_file.write(source_file.read())
                messagebox.showinfo("Download", "File downloaded successfully!")

    def play_tts_audio(self):
        if self.audio_file_path:
            pygame.mixer.music.load(str(self.audio_file_path))
            pygame.mixer.music.play()

    def play_audio(self):
        if self.audio_file_path:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            elif not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(str(self.audio_file_path))
                pygame.mixer.music.play()

    def pause_audio(self):
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.is_paused = False

if __name__ == "__main__":
    app = Application()
    app.mainloop()