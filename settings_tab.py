from tkinter import Frame, Canvas, Entry, Listbox, Scrollbar, Text, Button, PhotoImage, BooleanVar, Checkbutton, ttk
from pathlib import Path
import service
import main

class SettingsTab(Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()
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


        # OTP 인증키 입력 필드와 라벨
        self.otp_key_entry_image = PhotoImage(file=relative_to_assets("entry_11.png"))
        self.otp_key_entry_bg = self.canvas.create_image(158.0, 35.5, image=self.otp_key_entry_image)
        self.otp_key_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.otp_key_entry.place(x=102.0, y=27.0, width=112.0, height=15.0)
        self.canvas.create_text(30.0, 29.0, anchor="nw", text="OTP 인증키", fill="#000000", font=("Inter Bold", 12 * -1))
        
        # 실행 버튼
        self.execute_button_image = PhotoImage(file=relative_to_assets("button_5.png"))
        self.execute_button = Button(self.canvas, image=self.execute_button_image, borderwidth=0, highlightthickness=0, command=self.run_main, relief="flat")
        self.execute_button.place(x=228.0, y=24.0, width=37.0, height=22.0)

        # OPENAI API 키 입력 필드와 라벨
        self.openai_api_key_entry_image = PhotoImage(file=relative_to_assets("entry_10.png"))
        self.openai_api_key_entry_bg = self.canvas.create_image(185.5, 81.5, image=self.openai_api_key_entry_image)
        self.openai_api_key_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.openai_api_key_entry.place(x=102.0, y=73.0, width=167.0, height=15.0)
        self.canvas.create_text(32.0, 66.0, anchor="nw", text="OPENAI\nAPI 키", fill="#000000", font=("Inter Bold", 12 * -1))

        ######################### 네이버 계정 정보 #########################
         
        # 네이버 계정 정보 표시 영역 사각형 (탭 배경)
        self.canvas.create_rectangle(
            28.0,
            147.0,
            467.0,
            290.0,
            fill="#D9D9D9",
            outline="#000000")
        
        # 네이버 계정정보 라벨
        self.canvas.create_text(28.0, 125.0, anchor="nw", text="네이버 계정정보", fill="#000000", font=("Inter Bold", 12 * -1))

        # 로그인 ID 입력 필드와 라벨
        self.login_id_entry_image = PhotoImage(file=relative_to_assets("entry_9.png"))
        self.login_id_entry_bg = self.canvas.create_image(158.0, 192.5, image=self.login_id_entry_image)
        self.login_id_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.login_id_entry.place(x=102.0, y=184.0, width=112.0, height=15.0)
        self.canvas.create_text(36.0, 184.0, anchor="nw", text="로그인ID", fill="#000000", font=("Inter", 12 * -1))

        # 비밀번호 입력 필드와 라벨
        self.password_entry_image = PhotoImage(file=relative_to_assets("entry_8.png"))
        self.password_entry_bg = self.canvas.create_image(158.0, 220.5, image=self.password_entry_image)
        self.password_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.password_entry.place(x=102.0, y=212.0, width=112.0, height=15.0)
        self.canvas.create_text(36.0, 213.0, anchor="nw", text="비밀번호", fill="#000000", font=("Inter", 12 * -1))

        # 닉네임 입력 필드와 라벨
        self.nickname_entry_image = PhotoImage(file=relative_to_assets("entry_7.png"))
        self.nickname_entry_bg = self.canvas.create_image(158.0, 246.5, image=self.nickname_entry_image)
        self.nickname_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.nickname_entry.place(x=102.0, y=238.0, width=112.0, height=15.0)
        self.canvas.create_text(36.0, 240.0, anchor="nw", text="닉네임", fill="#000000", font=("Inter", 12 * -1))

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
        self.add_account_button.place(x=228.0, y=192.0, width=37.0, height=22.0)

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
        self.delete_account_button.place(x=228.0, y=224.0, width=37.0, height=22.0)

        # '추가된 계정정보' Listbox 설정
        self.account_info_listbox = Listbox(self, bg="#AAA2A2", fg="#000716")
        self.account_info_listbox.place(x=281.0, y=168.0, width=178.0, height=112.0)
        self.canvas.create_text(281.0, 153.0, anchor="nw", text="추가된 계정정보", fill="#000000", font=("Inter", 12 * -1))

        # '추가' 버튼 동작 설정
        self.add_account_button.config(command=self.add_account)

        # '삭제' 버튼 동작 설정
        self.delete_account_button.config(command=self.delete_account)
        
        # 스크롤바 생성 (처음에는 숨김)
        self.y_scrollbar = Scrollbar(self, command=self.account_info_listbox.yview)
        self.x_scrollbar = Scrollbar(self, orient="horizontal", command=self.account_info_listbox.xview)

        self.account_info_listbox.config(yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)

        ######################### 네이버 계정 정보 #########################

                     
        # 댓글에 추가할 문구 텍스트 필드와 라벨
        self.additional_comment_text_image = PhotoImage(file=relative_to_assets("entry_5.png"))
        self.additional_comment_text_bg = self.canvas.create_image(244.5, 366.0, image=self.additional_comment_text_image)
        self.additional_comment_text = Text(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.additional_comment_text.place(x=29.0, y=315.0, width=431.0, height=100.0)
        self.canvas.create_text(29.0, 298.0, anchor="nw", text="댓글에 추가할 문구", fill="#000000", font=("Inter Bold", 12 * -1))


        ######################### 서로이웃 피드 #########################

        # 서로이웃 피드 사각형 (탭 배경)
        self.canvas.create_rectangle(
            28.0,
            428.0,
            234.0,
            620.0,
            fill="#D9D9D9",
            outline="#000000")
        
        # 서로이웃 피드 체크박스 설정
        self.neighbor_feed_var = BooleanVar()
        self.neighbor_feed_chkbox = Checkbutton(
            self.canvas,
            text="서로이웃 피드 블로그 \n글에 댓글 및 좋아요",
            highlightthickness=0,
            variable=self.neighbor_feed_var,
            onvalue=True,
            offvalue=False,
            bg="#D9D9D9",
            activebackground="#D9D9D9",  # 활성화 시 배경색 설정
            command=lambda: print("Neighbor feed checkbox clicked, value:", self.neighbor_feed_var.get())
        )
        self.neighbor_feed_chkbox.place(x=56.0, y=437.0)  # 위치와 크기 조정
        # self.canvas.create_text(56.0, 436.0, anchor="nw", text="서로이웃 피드 블로그 \n글에 댓글 및 좋아요", fill="#000000", font=("Inter", 12 * -1))


        # 피드에서 추출할 글 개수 입력 필드와 라벨
        self.feed_extract_count_entry_image = PhotoImage(file=relative_to_assets("entry_4.png"))
        self.feed_extract_count_entry_bg = self.canvas.create_image(72.5, 527.5, image=self.feed_extract_count_entry_image)
        self.feed_extract_count_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.feed_extract_count_entry.place(x=36.0, y=519.0, width=73.0, height=15.0)
        self.canvas.create_text(36.0, 487.0, anchor="nw", text="피드에서 \n추출할 글 개수", fill="#000000", font=("Inter", 12 * -1))
        
        ######################### 서로이웃 피드 #########################


        ######################### 키워드 검색 #########################

        # 키워드 검색 사각형 (탭 배경)
        self.canvas.create_rectangle(
            248.0, 428.0, 454.0, 620.0,
            fill="#D9D9D9",
            outline="#000000"
        )
        
        # 키워드 검색 체크박스 설정
        self.keyword_search_var = BooleanVar()
        self.keyword_search_chkbox = Checkbutton(
            self.canvas,
            text="키워드 검색 결과 블로그 \n글에 댓글 및 좋아요",
            highlightthickness=0,
            variable=self.keyword_search_var,
            onvalue=True,
            offvalue=False,
            bg="#D9D9D9",  # 배경색 설정
            activebackground="#D9D9D9",  # 활성화 시 배경색 설정
            command=lambda: print("Keyword search checkbox clicked, value:", self.keyword_search_var.get())
        )
        self.keyword_search_chkbox.place(x=269.0, y=436.0)
        # self.canvas.create_text(269.0, 436.0, anchor="nw", text="키워드 검색 결과 블로그 \n글에 댓글 및 좋아요", fill="#000000", font=("Inter", 12 * -1))
        
        # 검색할 키워드 입력 필드와 라벨
        self.keyword_search_entry_image = PhotoImage(file=relative_to_assets("entry_3.png"))
        self.keyword_search_entry_bg = self.canvas.create_image(342.0, 504.5, image=self.keyword_search_entry_image)
        self.keyword_search_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.keyword_search_entry.place(x=263.0, y=496.0, width=158.0, height=15.0)
        self.canvas.create_text(265.0, 479.0, anchor="nw", text="검색할 키워드", fill="#000000", font=("Inter", 12 * -1))

        # 키워드로 추출할 글 개수 입력 필드와 라벨
        self.keyword_count_entry_image = PhotoImage(file=relative_to_assets("entry_2.png"))
        self.keyword_count_entry_bg = self.canvas.create_image(299.0, 551.5, image=self.keyword_count_entry_image)
        self.keyword_count_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.keyword_count_entry.place(x=263.0, y=543.0, width=72.0, height=15.0)
        self.canvas.create_text(265.0, 526.0, anchor="nw", text="키워드로 추출할 글 개수", fill="#000000", font=("Inter", 12 * -1))

        # 키워드 검색 정렬 콤보박스와 라벨
        self.keyword_sort_combobox = ttk.Combobox(self, values=["최신순", "정확도순"], state="readonly")
        self.keyword_sort_combobox.place(x=264.0, y=590.0, width=71.0, height=15.0)
        self.keyword_sort_combobox.set("최신순")  # 기본값 설정
        self.canvas.create_text(265.0, 573.0, anchor="nw", text="키워드 검색 정렬", fill="#000000", font=("Inter", 12 * -1))
 
        ######################### 키워드 검색 #########################



    ########################################################################
    ##########################  함수  ########################
    ########################################################################
        
    def run_main(self):
        main.main()

    def update_scrollbars(self):
        item_count = self.account_info_listbox.size()
        max_item_width = max([self.account_info_listbox.cget('width'), *(len(self.account_info_listbox.get(idx)) for idx in range(item_count))])

        # 세로 스크롤바 업데이트
        if item_count > 6:
            self.y_scrollbar.place(x=459.0, y=168.0, height=112.0)
        else:
            self.y_scrollbar.place_forget()

        # 가로 스크롤바 업데이트
        if max_item_width > self.account_info_listbox.cget('width'):
            self.x_scrollbar.place(x=281.0, y=280.0, width=178.0)
        else:
            self.x_scrollbar.place_forget()

    def add_account(self):
        login_id = self.login_id_entry.get()
        password = self.password_entry.get()
        nickname = self.nickname_entry.get()

        if service.validate_and_add_account(self.account_info_listbox, login_id, password, nickname):
            self.login_id_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.nickname_entry.delete(0, 'end')
            self.update_scrollbars()

    def delete_account(self):
        service.delete_selected_account_from_listbox(self.account_info_listbox)
        self.update_scrollbars()


    # 계정 정보를 리스트로 반환하는 메소드
    def get_account_info(self):
        accounts = []
        for idx in range(self.account_info_listbox.size()):
            account = self.account_info_listbox.get(idx)
            accounts.append(account.split(', '))
        return accounts




