import os
import threading
from tkinter import messagebox, scrolledtext
import onetimepass as otp
import tkinter as tk
from tkinter import Frame, Canvas, Entry, Listbox, Scrollbar, Text, Button, PhotoImage, BooleanVar, Checkbutton, ttk
from pathlib import Path
from ConfigManager import ConfigManager
import service
import main

class SettingsTab(Frame):
    PLACEHOLDER_OTP = '6자리 숫자'
    PLACEHOLDER_API_KEY = 'sk-'
    PLACEHOLDER_LOGIN_ID = '네이버 로그인ID'
    PLACEHOLDER_PASSWORD = '비밀번호'
    PLACEHOLDER_NICKNAME = '블로그 계정 닉네임'
    PLACEHOLDER_FEED_COUNT = '숫자 입력'
    PLACEHOLDER_KEYWORD = '키워드 입력'
    PLACEHOLDER_KEYWORD_COUNT = '숫자 입력'
    PLACEHOLDER_ADDITIONAL_COMMENT = 'AI로 생성된 댓글 뒤에 추가할 문구를 입력해주세요 (생략 가능)'

    def __init__(self, master=None, notebook=None, results_tab=None, **kwargs):
        super().__init__(master, **kwargs)
        self.notebook = notebook
        self.results_tab = results_tab
        self.is_running = False
        self.initialized = False  # 체크박스 2개 첫 로딩시 알림 안뜨게
        self.create_widgets()
        self.config_manager = ConfigManager("설정정보.ini")
        if os.path.exists("설정정보.ini"):
            self.load_settings()
        self.chkbox_activation()
        self.add_placeholders()
        self.update_scrollbars()  # 초기 스크롤바 상태 업데이트


    def create_widgets(self):
        # 경로 설정
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path("./build/assets/frame0")

        # 상대 경로 헬퍼 함수
        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)

        # 캔버스 설정
        self.canvas = Canvas(
            self,
            bg="#D1D1D1",
            height=644,
            width=495,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.pack(fill="both", expand=True)


        # 'OTP 인증키' 입력 필드와 라벨
        self.otp_key_entry_image = PhotoImage(file=relative_to_assets("entry_11.png"))
        self.otp_key_entry_bg = self.canvas.create_image(178.0, 35.5, image=self.otp_key_entry_image)
        self.otp_key_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.otp_key_entry.place(x=122.0, y=27.0, width=112.0, height=15.0)
        self.canvas.create_text(30.0, 29.0, anchor="nw", text="1. OTP 인증키", fill="#000000", font=("Inter Bold", 12 * -1))
        
        # '실행' 버튼
        self.execute_button_image = PhotoImage(file=relative_to_assets("button_5.png"))
        self.execute_button = Button(self.canvas, image=self.execute_button_image, borderwidth=0, highlightthickness=0, command=self.run_main, relief="flat")
        self.execute_button.place(x=248.0, y=24.0, width=37.0, height=22.0)

        # 안내 문구 추가
        # self.canvas.create_text(290.0, 35.0, anchor="nw", text="'실행'버튼을 누르면 자동으로 \n입력하신 \n데이터들이 저장됩니다.",fill="#000000",font=("Inter", 10))

        # 'OPENAI API 키' 입력 필드와 라벨
        self.openai_api_key_entry_image = PhotoImage(file=relative_to_assets("entry_10.png"))
        self.openai_api_key_entry_bg = self.canvas.create_image(205.5, 81.5, image=self.openai_api_key_entry_image)
        self.openai_api_key_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.openai_api_key_entry.place(x=122.0, y=73.0, width=167.0, height=15.0)
        self.canvas.create_text(30.0, 66.0, anchor="nw", text="2. OPENAI\nAPI 키", fill="#000000", font=("Inter Bold", 12 * -1))

        ###################################################################
        ######################### 네이버 계정 정보 #########################
         
        # 네이버 계정 정보 표시 영역 사각형 (탭 배경)
        self.canvas.create_rectangle(
            28.0,
            137.0,
            467.0,
            280.0,
            fill="#D9D9D9",
            outline="#000000")
        
        # '네이버 계정정보' 라벨
        self.canvas.create_text(28.0, 115.0, anchor="nw", text="3. 네이버 계정정보", fill="#000000", font=("Inter Bold", 12 * -1))

        # '로그인 ID' 입력 필드와 라벨
        self.login_id_entry_image = PhotoImage(file=relative_to_assets("entry_9.png"))
        self.login_id_entry_bg = self.canvas.create_image(158.0, 182.5, image=self.login_id_entry_image)
        self.login_id_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.login_id_entry.place(x=102.0, y=174.0, width=112.0, height=15.0)
        self.canvas.create_text(36.0, 174.0, anchor="nw", text="로그인ID", fill="#000000", font=("Inter", 12 * -1))

        # '비밀번호' 입력 필드와 라벨
        self.password_entry_image = PhotoImage(file=relative_to_assets("entry_8.png"))
        self.password_entry_bg = self.canvas.create_image(158.0, 210.5, image=self.password_entry_image)
        self.password_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.password_entry.place(x=102.0, y=202.0, width=112.0, height=15.0)
        self.canvas.create_text(36.0, 203.0, anchor="nw", text="비밀번호", fill="#000000", font=("Inter", 12 * -1))

        # '닉네임' 입력 필드와 라벨
        self.nickname_entry_image = PhotoImage(file=relative_to_assets("entry_7.png"))
        self.nickname_entry_bg = self.canvas.create_image(158.0, 236.5, image=self.nickname_entry_image)
        self.nickname_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.nickname_entry.place(x=102.0, y=228.0, width=112.0, height=15.0)
        self.canvas.create_text(36.0, 230.0, anchor="nw", text="닉네임", fill="#000000", font=("Inter", 12 * -1))

        # 계정 '추가' 버튼
        self.add_account_button_image = PhotoImage(file=relative_to_assets("button_4.png"))
        self.add_account_button = Button(
            self.canvas,
            image=self.add_account_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_4 clicked"),
            relief="flat"
        )
        self.add_account_button.place(x=228.0, y=182.0, width=37.0, height=22.0)

        # 계정 '삭제' 버튼
        self.delete_account_button_image = PhotoImage(file=relative_to_assets("button_3.png"))
        self.delete_account_button = Button(
            self.canvas,
            image=self.delete_account_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_3 clicked"),
            relief="flat"
        )
        self.delete_account_button.place(x=228.0, y=214.0, width=37.0, height=22.0)

        # '추가된 계정정보' Listbox 설정
        self.account_info_listbox = Listbox(self, bg="#AAA2A2", fg="#000716")
        self.account_info_listbox.place(x=281.0, y=158.0, width=178.0, height=112.0)
        self.canvas.create_text(281.0, 143.0, anchor="nw", text="추가된 계정정보", fill="#000000", font=("Inter", 12 * -1))

        # 계정 '위로' 버튼
        self.move_up_button = Button(self.canvas, text="▲", command=self.move_up)
        self.move_up_button.place(x=380.0, y=140.0, width=20, height=15)

        # 계정 '아래로' 버튼
        self.move_down_button = Button(self.canvas, text="▼", command=self.move_down)
        self.move_down_button.place(x=410.0, y=140.0, width=20, height=15)


        # '추가' 버튼 동작 설정
        self.add_account_button.config(command=self.add_account_to_listbox)

        # '삭제' 버튼 동작 설정
        self.delete_account_button.config(command=self.delete_account_from_listbox)
        
        # 스크롤바 생성 (처음에는 숨김)
        self.y_scrollbar = Scrollbar(self, command=self.account_info_listbox.yview)
        self.x_scrollbar = Scrollbar(self, orient="horizontal", command=self.account_info_listbox.xview)

        self.account_info_listbox.config(yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)

        ######################### 네이버 계정 정보 #########################
        ###################################################################
                     
        # '댓글에 추가할 문구' 텍스트 필드와 라벨
        self.additional_comment_text_image = PhotoImage(file=relative_to_assets("entry_5.png"))
        self.additional_comment_text_bg = self.canvas.create_image(244.5, 356.0, image=self.additional_comment_text_image)
        self.additional_comment_text = scrolledtext.ScrolledText(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.additional_comment_text.place(x=29.0, y=305.0, width=431.0, height=100.0)
        self.canvas.create_text(29.0, 290.0, anchor="nw", text="4. 댓글에 추가할 문구 (선택)", fill="#000000", font=("Inter Bold", 12 * -1))

        ################################################################
        ######################### 서로이웃 피드 #########################

        # 서로이웃 피드 사각형 (탭 배경)
        self.canvas.create_rectangle(
            28.0,
            418.0,
            234.0,
            610.0,
            fill="#D9D9D9",
            outline="#000000")
        
        # '서로이웃 피드 체크박스' 설정
        self.neighbor_feed_chkbox_var = BooleanVar()
        self.neighbor_feed_chkbox = Checkbutton(
            self.canvas,
            text="서로이웃 피드 블로그 \n글에 댓글 및 좋아요",
            highlightthickness=0,
            variable=self.neighbor_feed_chkbox_var,
            onvalue=True,
            offvalue=False,
            bg="#D9D9D9",
            activebackground="#D9D9D9",  # 활성화 시 배경색 설정
            command=self.on_neighbor_feed_chkbox_toggle
        )
        self.neighbor_feed_chkbox.place(x=56.0, y=427.0)  # 위치와 크기 조정
        

        # '피드에서 추출할 글 개수' 입력 필드와 라벨
        self.feed_extract_count_entry_image = PhotoImage(file=relative_to_assets("entry_4.png"))
        self.feed_extract_count_entry_bg = self.canvas.create_image(72.5, 517.5, image=self.feed_extract_count_entry_image)
        self.feed_extract_count_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.feed_extract_count_entry.place(x=36.0, y=509.0, width=73.0, height=15.0)
        self.canvas.create_text(36.0, 477.0, anchor="nw", text="피드에서 \n추출할 글 개수", fill="#000000", font=("Inter", 12 * -1))
        
        ######################### 서로이웃 피드 #########################
        ################################################################

        ##############################################################
        ######################### 키워드 검색 #########################

        # 키워드 검색 사각형 (탭 배경)
        self.canvas.create_rectangle(
            248.0, 418.0, 454.0, 610.0,
            fill="#D9D9D9",
            outline="#000000"
        )
        
        # '키워드 검색 체크박스' 설정
        self.keyword_search_chkbox_var = BooleanVar()
        self.keyword_search_chkbox = Checkbutton(
            self.canvas,
            text="키워드 검색 결과 블로그 \n글에 댓글 및 좋아요",
            highlightthickness=0,
            variable=self.keyword_search_chkbox_var,
            onvalue=True,
            offvalue=False,
            bg="#D9D9D9",  # 배경색 설정
            activebackground="#D9D9D9",  # 활성화 시 배경색 설정
            command=self.on_keyword_search_chkbox_toggle
        )
        self.keyword_search_chkbox.place(x=269.0, y=426.0)
        
        # '검색할 키워드' 입력 필드와 라벨
        self.keyword_search_entry_image = PhotoImage(file=relative_to_assets("entry_3.png"))
        self.keyword_search_entry_bg = self.canvas.create_image(342.0, 494.5, image=self.keyword_search_entry_image)
        self.keyword_search_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.keyword_search_entry.place(x=263.0, y=486.0, width=158.0, height=15.0)
        self.canvas.create_text(265.0, 469.0, anchor="nw", text="검색할 키워드", fill="#000000", font=("Inter", 12 * -1))

        # '키워드로 추출할 글 개수' 입력 필드와 라벨
        self.keyword_count_entry_image = PhotoImage(file=relative_to_assets("entry_2.png"))
        self.keyword_count_entry_bg = self.canvas.create_image(299.0, 541.5, image=self.keyword_count_entry_image)
        self.keyword_count_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.keyword_count_entry.place(x=263.0, y=533.0, width=72.0, height=15.0)
        self.canvas.create_text(265.0, 516.0, anchor="nw", text="키워드로 추출할 글 개수", fill="#000000", font=("Inter", 12 * -1))

        # '키워드 검색 정렬' 콤보박스와 라벨
        self.keyword_sort_combobox = ttk.Combobox(self, values=["최신순", "정확도순"], state="readonly")
        self.keyword_sort_combobox.place(x=264.0, y=580.0, width=71.0, height=20.0)
        self.keyword_sort_combobox.set("최신순")  # 기본값 설정
        self.canvas.create_text(265.0, 563.0, anchor="nw", text="키워드 검색 정렬", fill="#000000", font=("Inter", 12 * -1))
 
        ######################### 키워드 검색 #########################
        ##############################################################

        self.initialized = True

    ########################################################################
    ###############################  함수  #################################
    ########################################################################
        
    def run_main(self):
        self.save_settings()

        # 유효성 검사
        if not self.validate_inputs():
            return
        
        otp_key = self.otp_key_entry.get()
        if not self.validate_otp(otp_key):
            return

        # '실행' 버튼 비활성화
        self.is_running = True
        self.execute_button.config(state="disabled")

        # 사용자 입력 데이터 수집
        user_input_data = self.get_user_input_datas()

        # main_logic 함수를 별도의 스레드에서 실행
        main_logic_thread = threading.Thread(
            target=self.execute_main_logic, 
            args=(user_input_data)
        )
        main_logic_thread.start()

    def validate_otp(self, user_code):
        secret_key = 'DIOFEPCKNMKOLEJFOSJOEHIUZHEBNKAL'
        user_code = user_code.replace(" ", "")  # 띄어쓰기 및 공백 제거
        if otp.valid_totp(token=user_code, secret=secret_key):
            print('------- 프로그램 인증에 성공하였습니다. -------')
            return True
        else:
            messagebox.showinfo("인증 실패", "OTP 인증키가 올바르지 않습니다. 다시 시도해주세요.")
            self.otp_key_entry.focus_set()
            return False
                
    def execute_main_logic(self, api_key, additional_comment, account_infos, feed_blog_count, keyword, keyword_blog_count, sorting_preference):
       # '실행 결과' 탭으로 전환
        if self.notebook and self.results_tab:
            results_tab_index = self.notebook.index(self.results_tab)
            self.notebook.select(results_tab_index)

        # main_logic 함수 호출
        main.main_logic(api_key, additional_comment, 
                        account_infos, feed_blog_count, keyword, 
                        keyword_blog_count, sorting_preference)
        
        # 다 끝나면 '실행' 버튼 활성화
        self.is_running = False
        self.execute_button.config(state="active")  

    def get_user_input_datas(self):
        api_key = self.openai_api_key_entry.get()
        account_infos = [self.account_info_listbox.get(idx) for idx in range(self.account_info_listbox.size())]
        additional_comment = self.additional_comment_text.get("1.0", "end-1c")
        
        # 'neighbor_feed_chkbox' 해제 -> '피드에서 추출할 글 개수' = 0
        feed_blog_count = int(self.feed_extract_count_entry.get()) if self.feed_extract_count_entry['state'] != 'disabled' else 0
        
        # 'keyword_search_chkbox' 해제 -> 관련 위젯3개 값 None Or 0
        keyword = self.keyword_search_entry.get() if self.keyword_search_entry['state'] != 'disabled' else None
        keyword_blog_count = int(self.keyword_count_entry.get()) if self.keyword_count_entry['state'] != 'disabled' else 0
        sorting_preference = self.keyword_sort_combobox.get() if self.keyword_sort_combobox['state'] != 'disabled' else None

        return (api_key, additional_comment, account_infos, 
                feed_blog_count, keyword, keyword_blog_count, sorting_preference)

    # 서로이웃 피드 관련 활성화/비활성화
    def on_neighbor_feed_chkbox_toggle(self):
        if self.neighbor_feed_chkbox_var.get():
            self.feed_extract_count_entry.config(state="normal")
        else:
            self.feed_extract_count_entry.config(state="disabled")

    # 키워드 검색 관련 활성화/비활성화
    def on_keyword_search_chkbox_toggle(self):
        if self.keyword_search_chkbox_var.get():
            self.keyword_search_entry.config(state="normal")
            self.keyword_count_entry.config(state="normal")
            self.keyword_sort_combobox.config(state="readonly")
        else:
            self.keyword_search_entry.config(state="disabled")
            self.keyword_count_entry.config(state="disabled")
            self.keyword_sort_combobox.config(state="disabled")

    def on_neighbor_feed_chkbox_changed(self, *args):
        if not self.initialized:
            return
       
        if not self.neighbor_feed_chkbox_var.get() and not self.keyword_search_chkbox_var.get():
            self.neighbor_feed_chkbox_var.set(True)
            messagebox.showwarning("안내", "'서로이웃 피드' 또는 '키워드 검색' 체크박스 중 하나는 활성화되어야 합니다.")

    def on_keyword_search_chkbox_changed(self, *args):
        if not self.initialized:
            return
                
        if not self.neighbor_feed_chkbox_var.get() and not self.keyword_search_chkbox_var.get():
            self.keyword_search_chkbox_var.set(True)
            messagebox.showwarning("안내", "'서로이웃 피드' 또는 '키워드 검색' 체크박스 중 하나는 활성화되어야 합니다.")
            

    def validate_inputs(self):
        # 'OTP 인증키' 검사
        otp_key = self.otp_key_entry.get()
        if not otp_key or otp_key == self.PLACEHOLDER_OTP:
            messagebox.showwarning("안내", "OTP 인증키를 입력해주세요.")
            self.otp_key_entry.focus_set()
            return False

        if not otp_key.isdigit():
            messagebox.showwarning("안내", "OTP 인증키는 숫자로만 구성되어야 합니다.")
            self.otp_key_entry.focus_set()
            return False

        # 'OPENAI API 키' 검사
        api_key = self.openai_api_key_entry.get()
        if not api_key or api_key == self.PLACEHOLDER_API_KEY:
            messagebox.showwarning("안내", "'OPENAI API 키'를 입력해주세요.")
            self.openai_api_key_entry.focus_set()
            return False

        if not api_key.startswith('sk-'):
            messagebox.showwarning("안내", "'OPENAI API 키'가 'sk-'로 시작해야 합니다.")
            self.openai_api_key_entry.focus_set()
            return False

        # '추가된 계정정보' Listbox 검사
        if self.account_info_listbox.size() == 0:
            messagebox.showwarning("안내", "최소 한 쌍의 계정 정보가 필요합니다. '추가된 계정정보'란에 계정정보를 추가해주세요.")
            return False

        # '서로이웃 피드' 입력 검사
        if self.neighbor_feed_chkbox_var.get():
            feed_blog_count_str = self.feed_extract_count_entry.get()
            if not feed_blog_count_str or feed_blog_count_str == self.PLACEHOLDER_FEED_COUNT:
                messagebox.showwarning("안내", "'피드에서 추출할 글 개수'를 입력해주세요.")
                self.feed_extract_count_entry.focus_set()
                return False
            
            try:
                feed_blog_count = int(feed_blog_count_str)
            except ValueError:
                messagebox.showwarning("안내", "'피드에서 추출할 글 개수'는 숫자여야 합니다.")
                self.feed_extract_count_entry.focus_set()
                return False

        # '키워드 검색' 입력 검사
        if self.keyword_search_chkbox_var.get():
            keyword = self.keyword_search_entry.get()
            if not keyword or keyword == self.PLACEHOLDER_KEYWORD:
                messagebox.showwarning("안내", "'검색할 키워드'를 입력해주세요.")
                self.keyword_search_entry.focus_set()
                return False

            keyword_blog_count_str = self.keyword_count_entry.get()
            if not keyword_blog_count_str or keyword_blog_count_str == self.PLACEHOLDER_KEYWORD_COUNT:
                messagebox.showwarning("안내", "'키워드로 추출할 글 개수'를 입력해주세요.")
                self.keyword_count_entry.focus_set()
                return False
            
            try:
                keyword_blog_count = int(keyword_blog_count_str)
            except ValueError:
                messagebox.showwarning("안내", "'키워드로 추출할 글 개수'는 숫자여야 합니다.")
                self.keyword_count_entry.focus_set()
                return False

            if keyword_blog_count <= 0:
                messagebox.showwarning("안내", "'키워드로 추출할 글 개수'는 1 이상이어야 합니다.")
                self.keyword_count_entry.focus_set()
                return False

        # '댓글에 추가할 문구' 입력 검사
        additional_comment = self.additional_comment_text.get("1.0", "end-1c")
        if additional_comment == self.PLACEHOLDER_ADDITIONAL_COMMENT:
            additional_comment = ''

        return True


    def update_scrollbars(self):
        item_count = self.account_info_listbox.size()
        max_item_width = max([self.account_info_listbox.cget('width'), *(len(self.account_info_listbox.get(idx)) for idx in range(item_count))])
        
        if item_count > 6:  # 세로 스크롤바 업데이트
            self.y_scrollbar.place(x=459.0, y=158.0, height=112.0)
        else:
            self.y_scrollbar.place_forget()
        
        if max_item_width > self.account_info_listbox.cget('width'):    # 가로 스크롤바 업데이트
            self.x_scrollbar.place(x=281.0, y=270.0, width=178.0)
        else:
            self.x_scrollbar.place_forget()


    def add_account_to_listbox(self):
        login_id = self.login_id_entry.get()
        password = self.password_entry.get()
        nickname = self.nickname_entry.get()

        if service.validate_and_add_account(self.account_info_listbox, login_id, password, nickname):
            self.login_id_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.nickname_entry.delete(0, 'end')
            self.update_scrollbars()


    def delete_account_from_listbox(self):
        service.delete_selected_account_from_listbox(self.account_info_listbox)
        self.update_scrollbars()


    def move_up(self):
        selected = self.account_info_listbox.curselection()
        if selected:
            index = selected[0]
            if index > 0:
                item = self.account_info_listbox.get(index)
                self.account_info_listbox.delete(index)
                self.account_info_listbox.insert(index - 1, item)
                self.account_info_listbox.select_set(index - 1)

    def move_down(self):
        selected = self.account_info_listbox.curselection()
        if selected:
            index = selected[0]
            if index < self.account_info_listbox.size() - 1:
                item = self.account_info_listbox.get(index)
                self.account_info_listbox.delete(index)
                self.account_info_listbox.insert(index + 1, item)
                self.account_info_listbox.select_set(index + 1)


    def add_placeholder_to_entry(self, entry_widget, placeholder, placeholder_color="#454343"):  
        def on_focus_in(event, placeholder=placeholder):
            if entry_widget.get() == placeholder:
                entry_widget.delete(0, tk.END)
                entry_widget.config(fg='black')

        def on_focus_out(event, placeholder=placeholder):
            if entry_widget.get() == '':
                entry_widget.insert(0, placeholder)
                entry_widget.config(fg=placeholder_color)

        if entry_widget.get() == '':
            entry_widget.insert(0, placeholder)
            entry_widget.config(fg=placeholder_color)

        entry_widget.bind("<FocusIn>", on_focus_in)
        entry_widget.bind("<FocusOut>", on_focus_out)


    def add_placeholder_to_text(self, text_widget, placeholder, placeholder_color="#454343"): 
        def on_focus_in(event, placeholder=placeholder):
            if text_widget.get("1.0", tk.END).strip() == placeholder:
                text_widget.delete("1.0", tk.END)
                text_widget.config(fg='black')

        def on_focus_out(event, placeholder=placeholder):
            if text_widget.get("1.0", tk.END).strip() == '':
                text_widget.insert("1.0", placeholder)
                text_widget.config(fg=placeholder_color)

        if text_widget.get("1.0", tk.END).strip() == '':
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg=placeholder_color)

        text_widget.bind("<FocusIn>", on_focus_in)
        text_widget.bind("<FocusOut>", on_focus_out)


    def add_placeholders(self):
        self.add_placeholder_to_entry(self.otp_key_entry, self.PLACEHOLDER_OTP)
        self.add_placeholder_to_entry(self.openai_api_key_entry, self.PLACEHOLDER_API_KEY)
        self.add_placeholder_to_entry(self.login_id_entry, self.PLACEHOLDER_LOGIN_ID)
        self.add_placeholder_to_entry(self.password_entry, self.PLACEHOLDER_PASSWORD)
        self.add_placeholder_to_entry(self.nickname_entry, self.PLACEHOLDER_NICKNAME)
        self.add_placeholder_to_entry(self.feed_extract_count_entry, self.PLACEHOLDER_FEED_COUNT)
        self.add_placeholder_to_entry(self.keyword_search_entry, self.PLACEHOLDER_KEYWORD)
        self.add_placeholder_to_entry(self.keyword_count_entry, self.PLACEHOLDER_KEYWORD_COUNT)
        self.add_placeholder_to_text(self.additional_comment_text, self.PLACEHOLDER_ADDITIONAL_COMMENT)


    def chkbox_activation(self):
        self.on_keyword_search_chkbox_toggle()
        self.on_neighbor_feed_chkbox_toggle()

        self.neighbor_feed_chkbox_var.trace_add('write', self.on_neighbor_feed_chkbox_changed)
        self.keyword_search_chkbox_var.trace_add('write', self.on_keyword_search_chkbox_changed)


    def load_settings(self):
        
        api_key = self.config_manager.load_config('실행정보', 'openai api 키')
        self.openai_api_key_entry.insert(0, api_key)

        accounts_str = self.config_manager.load_config('실행정보', '추가된 계정정보')
        if accounts_str:
            accounts = accounts_str.split('\n')
            for account in accounts:
                self.account_info_listbox.insert(tk.END, account)

        additional_comment = self.config_manager.load_config('실행정보', '댓글에 추가할 문구')
        self.additional_comment_text.insert('1.0', additional_comment)

        neighbor_feed_chkbox_value = self.config_manager.load_config('실행정보', '서로이웃 피드 체크박스')
        self.neighbor_feed_chkbox_var.set(neighbor_feed_chkbox_value == 'True')
        
        feed_blog_count = self.config_manager.load_config('실행정보', '피드에서 추출할 글 개수')
        self.feed_extract_count_entry.insert(0, feed_blog_count)

        keyword_search_chkbox_value = self.config_manager.load_config('실행정보', '키워드 검색 체크박스')
        self.keyword_search_chkbox_var.set(keyword_search_chkbox_value == 'True')

        keyword = self.config_manager.load_config('실행정보', '검색할 키워드')
        self.keyword_search_entry.insert(0, keyword)

        keyword_blog_count = self.config_manager.load_config('실행정보', '키워드로 추출할 글 개수')
        self.keyword_count_entry.insert(0, keyword_blog_count)

        sorting_preference = self.config_manager.load_config('실행정보', '키워드 검색 정렬')
        self.keyword_sort_combobox.set(sorting_preference)
    

    def save_settings(self):
        api_key = self.openai_api_key_entry.get()
        self.config_manager.save_config('실행정보', 'OPENAI API 키', api_key)

        accounts = [self.account_info_listbox.get(idx) for idx in range(self.account_info_listbox.size())]
        accounts_str = '\n'.join(accounts)
        self.config_manager.save_config('실행정보', '추가된 계정정보', accounts_str)

        additional_comment = self.additional_comment_text.get("1.0", "end-1c")
        self.config_manager.save_config('실행정보', '댓글에 추가할 문구', additional_comment)

        self.config_manager.save_config('실행정보', '서로이웃 피드 체크박스', 
                                        str(self.neighbor_feed_chkbox_var.get()))

        feed_blog_count = self.feed_extract_count_entry.get()
        self.config_manager.save_config('실행정보', '피드에서 추출할 글 개수', feed_blog_count)

        self.config_manager.save_config('실행정보', '키워드 검색 체크박스', 
                                        str(self.keyword_search_chkbox_var.get()))

        keyword = self.keyword_search_entry.get()
        self.config_manager.save_config('실행정보', '검색할 키워드', keyword)

        keyword_blog_count = self.keyword_count_entry.get()
        self.config_manager.save_config('실행정보', '키워드로 추출할 글 개수', keyword_blog_count)

        sorting_preference = self.keyword_sort_combobox.get()
        self.config_manager.save_config('실행정보', '키워드 검색 정렬', sorting_preference)


