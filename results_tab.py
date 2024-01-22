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
        self.result_text = scrolledtext.ScrolledText(self, height=50)
        self.result_text.pack(pady=0)

        # 사용자의 입력을 무시하되, 복사는 허용
        self.result_text.bind("<Key>", lambda e: "break")
        self.result_text.bind("<Control-c>", self.copy_text)
        self.result_text.bind("<Command-c>", self.copy_text)  # 맥 사용자의 경우

    def copy_text(self, event):
        # 선택된 텍스트를 복사하는 함수
        try:
            self.result_text.clipboard_clear()
            text = self.result_text.get("sel.first", "sel.last")
            self.result_text.clipboard_append(text)
        except tk.TclError:
            pass  # 선택된 텍스트가 없으면 아무것도 하지 않음
        return "break"  # 기본 이벤트 처리 중단