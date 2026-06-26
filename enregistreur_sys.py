import customtkinter as ctk
from tkinter import filedialog, messagebox
import sounddevice as sd
import numpy as np
import threading
import queue
import os
import time
import wave
import sys
import platform
import subprocess

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    def rtl_text(text):
        if not isinstance(text, str):
            text = str(text)
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
except ImportError:
    def rtl_text(text):
        return text

# إعدادات CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class VoiceRecorderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("مسجل صوت النظام مع كشف الصوت التلقائي")
        self.geometry("600x450")
        self.minsize(600, 450)

        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.fs = 44100  # تردد العينة
        self.channels = 2  # 2 للقناة الاستريو لنظام الصوت
        self.frames = []
        self.stream = None
        self.folder_path = os.path.expanduser("~")  # مجلد الحفظ الافتراضي

        self.build_ui()
        self.log("تم بدء البرنامج")

    def build_ui(self):
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", pady=10, padx=10)

        self.btn_choose_folder = ctk.CTkButton(top_frame, text=rtl_text("📁 اختيار مجلد الحفظ"), command=self.choose_folder, fg_color="#4a90e2", hover_color="#357ABD")
        self.btn_choose_folder.pack(side="left", padx=5)

        self.btn_open_folder = ctk.CTkButton(top_frame, text=rtl_text("📂 فتح مجلد الحفظ"), command=self.open_folder, fg_color="#4a90e2", hover_color="#357ABD")
        self.btn_open_folder.pack(side="left", padx=5)

        self.btn_start = ctk.CTkButton(top_frame, text=rtl_text("▶️ بدء التسجيل"), command=self.start_recording, fg_color="#27ae60", hover_color="#2ecc71")
        self.btn_start.pack(side="left", padx=10)

        self.btn_stop = ctk.CTkButton(top_frame, text=rtl_text("⛔ إيقاف التسجيل"), command=self.stop_recording, fg_color="#c0392b", hover_color="#e74c3c", state="disabled")
        self.btn_stop.pack(side="left", padx=10)

        self.recording_indicator = ctk.CTkLabel(top_frame, text="", text_color="red", font=ctk.CTkFont(size=24))
        self.recording_indicator.pack(side="left", padx=10)

        self.label_folder = ctk.CTkLabel(self, text=rtl_text("مجلد الحفظ: ") + self.folder_path, anchor="w")
        self.label_folder.pack(fill="x", padx=10)

        self.log_box = ctk.CTkTextbox(self, height=15, state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {rtl_text(message)}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_path)
        if folder:
            self.folder_path = folder
            self.label_folder.configure(text=rtl_text("مجلد الحفظ: ") + self.folder_path)
            self.log(f"تم اختيار مجلد الحفظ: {folder}")

    def open_folder(self):
        if not os.path.exists(self.folder_path):
            messagebox.showerror(rtl_text("خطأ"), rtl_text("مجلد الحفظ غير موجود."))
            return
        if platform.system() == "Windows":
            os.startfile(self.folder_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", self.folder_path])
        else:
            subprocess.Popen(["xdg-open", self.folder_path])
        self.log(f"تم فتح مجلد الحفظ: {self.folder_path}")

    def get_loopback_device(self):
        """ابحث عن جهاز صوت النظام (loopback) باستخدام WASAPI في ويندوز"""
        if platform.system() != "Windows":
            self.log("ميزة تسجيل صوت النظام متوفرة فقط على Windows")
            return None

        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        wasapi_index = None
        # البحث عن index الخاص ب WASAPI
        for idx, hostapi in enumerate(hostapis):
            if hostapi['name'] == 'Windows WASAPI':
                wasapi_index = idx
                break
        if wasapi_index is None:
            self.log("لم يتم العثور على واجهة WASAPI")
            return None

        # البحث عن جهاز يحتوي على "loopback" أو "mixage stéréo" أو "stereo mix" ضمن WASAPI ويدعم الإدخال
        for idx, dev in enumerate(devices):
            name_lower = dev['name'].lower()
            if dev['hostapi'] == wasapi_index and dev['max_input_channels'] > 0 and ('loopback' in name_lower or 'mixage stéréo' in name_lower or 'stereo mix' in name_lower):
                self.log(f"تم تحديد جهاز تسجيل: {dev['name']}")
                return idx
        self.log("لم يتم العثور على جهاز loopback لنظام الصوت")
        return None

    def start_recording(self):
        if self.is_recording:
            self.log("التسجيل جارٍ بالفعل")
            return

        device_index = self.get_loopback_device()
        if device_index is None:
            messagebox.showerror(rtl_text("خطأ"), rtl_text("لم يتم العثور على جهاز تسجيل صوت النظام (loopback). تأكد من تشغيل Windows WASAPI وأن جهاز الصوت يدعم ذلك."))
            return

        self.is_recording = True
        self.frames = []
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.recording_indicator.configure(text="●")
        self.log("بدء التسجيل من صوت النظام...")

        def audio_callback(indata, frames, time_, status):
            if status:
                self.log(f"⚠️ {status}")
            volume_norm = np.linalg.norm(indata) * 10
            if volume_norm > 5:  # حد اكتشاف الصوت
                self.log(f"تم الكشف عن صوت (شدة {volume_norm:.2f})")
            if self.is_recording:
                self.frames.append(indata.copy())

        def record_thread():
            try:
                with sd.InputStream(device=device_index, channels=self.channels, samplerate=self.fs, callback=audio_callback):
                    while self.is_recording:
                        sd.sleep(100)
            except Exception as e:
                self.log(f"خطأ أثناء التسجيل: {e}")
                self.is_recording = False
                self.btn_start.configure(state="normal")
                self.btn_stop.configure(state="disabled")
                self.recording_indicator.configure(text="")

        threading.Thread(target=record_thread, daemon=True).start()

    def stop_recording(self):
        if not self.is_recording:
            self.log("لم يتم بدء التسجيل")
            return
        self.is_recording = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.recording_indicator.configure(text="")
        self.log("تم إيقاف التسجيل")

        # حفظ التسجيل بعد فترة قصيرة للسماح بالتوقف الكامل
        threading.Thread(target=self.save_recording).start()

    def save_recording(self):
        if not self.frames:
            self.log("لم يتم تسجيل أي صوت")
            return
        filename = time.strftime("recording_%Y%m%d_%H%M%S.wav")
        filepath = os.path.join(self.folder_path, filename)
        try:
            wf = wave.open(filepath, "wb")
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16 bit audio
            wf.setframerate(self.fs)
            audio_data = np.concatenate(self.frames)
            audio_data_int16 = (audio_data * 32767).astype(np.int16)  # تحويل float32 إلى int16
            audio_bytes = audio_data_int16.tobytes()
            wf.writeframes(audio_bytes)
            wf.close()
            self.log(f"تم حفظ التسجيل في الملف: {filepath}")
        except Exception as e:
            self.log(f"خطأ في حفظ الملف: {e}")

if __name__ == "__main__":
    app = VoiceRecorderApp()
    app.mainloop()