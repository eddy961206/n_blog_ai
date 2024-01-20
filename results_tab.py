import tkinter as tk
from tkinter import scrolledtext

class ResultsTab(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        # 실행 결과 레이블
        self.result_label = tk.Label(self, text="실행 결과")
        self.result_label.pack(pady=5)

        # 실행 결과 표시 영역
        self.result_text = scrolledtext.ScrolledText(self, height=20)
        self.result_text.pack(pady=5)
