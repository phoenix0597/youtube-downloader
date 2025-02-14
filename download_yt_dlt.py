import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import os
import threading


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x350")

        # URL input
        self.url_label = tk.Label(root, text="Введите URL видео:")
        self.url_label.pack(pady=10)

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # Check formats button
        self.check_formats_button = tk.Button(
            root, text="Проверить доступные форматы", command=self.check_formats
        )
        self.check_formats_button.pack(pady=5)

        # Format selection
        self.format_label = tk.Label(root, text="Выберите формат:")
        self.format_label.pack(pady=5)

        self.format_combobox = ttk.Combobox(root, width=47, state="disabled")
        self.format_combobox.pack(pady=5)

        # Path selection
        self.path_label = tk.Label(root, text="Путь для сохранения:")
        self.path_label.pack(pady=10)

        self.path_frame = tk.Frame(root)
        self.path_frame.pack(pady=5)

        self.path_entry = tk.Entry(self.path_frame, width=40)
        self.path_entry.pack(side=tk.LEFT, padx=5)

        self.browse_button = tk.Button(
            self.path_frame, text="Обзор", command=self.browse_path
        )
        self.browse_button.pack(side=tk.LEFT)

        # Download button
        self.download_button = tk.Button(
            root, text="Скачать", command=self.start_download, state="disabled"
        )
        self.download_button.pack(pady=20)

        # Progress label
        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack(pady=10)

        # Set default download path
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.path_entry.insert(0, default_path)

        # Store available formats
        self.formats = []

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)

    def check_formats(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Ошибка", "Пожалуйста, введите URL видео")
            return

        self.check_formats_button.config(state="disabled")
        self.progress_label.config(text="Получение списка форматов...")

        # Start format checking in a separate thread
        thread = threading.Thread(target=self.get_formats)
        thread.start()

    def get_formats(self):
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url_entry.get(), download=False)
                self.formats = []
                format_dict = {}

                # Собираем форматы с видео и аудио
                for f in info["formats"]:
                    if (
                        f.get("vcodec", "none") != "none"
                        and f.get("acodec", "none") != "none"
                    ):
                        format_str = (
                            f"{f['format_id']} - {f.get('ext', 'N/A')} - "
                            f"{f.get('resolution', 'N/A')} - "
                            f"Size: {f.get('filesize_approx', 'N/A')}"
                        )
                        self.formats.append(f)
                        format_dict[format_str] = f["format_id"]

                # Обновляем GUI в главном потоке
                self.root.after(0, self.update_formats_gui, format_dict)

        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            self.root.after(0, lambda: self.check_formats_button.config(state="normal"))

    def update_formats_gui(self, format_dict):
        self.format_combobox["values"] = list(format_dict.keys())
        self.format_combobox.set("Выберите формат")
        self.format_combobox.config(state="readonly")
        self.download_button.config(state="normal")
        self.progress_label.config(
            text="Форматы загружены. Выберите формат для скачивания."
        )

    def show_error(self, error_message):
        self.progress_label.config(text="Произошла ошибка!")
        messagebox.showerror("Ошибка", f"Произошла ошибка: {error_message}")

    def start_download(self):
        if self.format_combobox.get() == "Выберите формат":
            messagebox.showerror("Ошибка", "Пожалуйста, выберите формат")
            return
        download_thread = threading.Thread(target=self.download_video)
        download_thread.start()

    def progress_hook(self, d):
        if d["status"] == "downloading":
            try:
                percent = d.get("_percent_str", "N/A")
                speed = d.get("_speed_str", "N/A")
                self.progress_label.config(
                    text=f"Загрузка: {percent} (Скорость: {speed})"
                )
            except:
                pass
        elif d["status"] == "finished":
            self.progress_label.config(text="Загрузка завершена! Обработка файла...")

    def download_video(self):
        try:
            self.download_button.config(state="disabled")
            url = self.url_entry.get()
            path = self.path_entry.get()
            selected_format = self.format_combobox.get().split(" - ")[
                0
            ]  # Получаем format_id

            if not url or not path:
                messagebox.showerror(
                    "Ошибка", "Пожалуйста, введите URL и путь для сохранения"
                )
                return

            ydl_opts = {
                "format": selected_format,
                "outtmpl": os.path.join(path, "%(title)s.%(ext)s"),
                "progress_hooks": [self.progress_hook],
                "quiet": True,
                "no_warnings": True,
                "socket_timeout": 30,
                "retries": 10,
                "fragment_retries": 10,
                "http_chunk_size": 10485760,
                "ignoreerrors": True,
                "noprogress": False,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                },
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.progress_label.config(text="Загрузка завершена!")
            messagebox.showinfo("Успех", "Видео успешно скачано!")

        except Exception as e:
            self.progress_label.config(text="Произошла ошибка!")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

        finally:
            self.download_button.config(state="normal")


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
