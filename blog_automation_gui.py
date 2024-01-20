import tkinter as tk
from tkinter import ttk
from settings_tab import SettingsTab
from results_tab import ResultsTab

root = tk.Tk()
root.title("블로그 자동화 프로그램")
root.geometry("495x650")

tab_control = ttk.Notebook(root)

# '기본 설정' 탭 생성 및 추가
settings_tab = SettingsTab(tab_control)
tab_control.add(settings_tab, text='기본 설정')

# '실행 결과' 탭 생성 및 추가
results_tab = ResultsTab(tab_control)
tab_control.add(results_tab, text='실행 결과')

tab_control.pack(expand=1, fill='both')

root.mainloop()
