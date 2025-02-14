import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import os
import threading


class YouTubeDownloader:
    def init(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x250")

        # URL input
        self.url_label = tk.Label(root, text="Введите URL видео:")
        self.url_label.pack(pady=10)

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # Path selection
        self.path_label = tk.Label(root, text="Путь для сохранения:")
        self.path_label.pack(pady=10)

        self.path_frame = tk.Frame(root)
        self.path_frame.pack(pady=5)

        self.path_entry = tk.Entry(self.path_frame, width=40)
        self.path_entry.pack(side=tk.LEFT, padx=5)

        self.browse_button = tk.Button(self.path_frame, text="Обзор", command=self.browse_path)
        self.browse_button.pack(side=tk.LEFT)

        # Download button
        self.download_button = tk.Button(root, text="Скачать", command=self.start_download)
        self.download_button.pack(pady=20)

        # Progress label
        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack(pady=10)

        # Set default download path
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.path_entry.insert(0, default_path)

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)

    def start_download(self):
        download_thread = threading.Thread(target=self.download_video)
        download_thread.start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Обновляем информацию о прогрессе
            try:
                percent = d['_percent_str']
                speed = d['_speed_str']
                self.progress_label.config(text=f"Загрузка: {percent} (Скорость: {speed})")
            except:
                pass
        elif d['status'] == 'finished':
            self.progress_label.config(text="Загрузка завершена! Обработка файла...")

    def download_video(self):
        try:
            self.download_button.config(state=tk.DISABLED)
            url = self.url_entry.get()
            path = self.path_entry.get()

            if not url or not path:
                messagebox.showerror("Ошибка", "Пожалуйста, введите URL и путь для сохранения")
                self.download_button.config(state=tk.NORMAL)
                self.progress_label.config(text="")
                return

            ydl_opts = {
                'format': 'best',  # Лучшее качество видео
                'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),  # Шаблон имени файла
                'progress_hooks': [self.progress_hook],  # Функция для отслеживания прогресса
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.progress_label.config(text="Загрузка завершена!")
            messagebox.showinfo("Успех", "Видео успешно скачано!")

        except Exception as e:
            self.progress_label.config(text="Произошла ошибка!")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

        finally:
            self.download_button.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "main":
    main()