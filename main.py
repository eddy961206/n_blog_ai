import ctypes
from ctypes import wintypes
import sys
import time
from blog_actions import (read_account_data_from_xlsx, initialize_driver, 
                          fetch_single_data_from_account_datas, login_to_naver, 
                          get_blog_links, is_already_commented, 
                          like_blog_post, extract_blog_content, extract_author_name, 
                          generate_comment_with_ai, post_comment, logout_of_naver,
                          print_final_output)
from otp import validate_otp
from api import OpenAIChatClient


max_link_extract_cnt = 100
likeminPauseTime = 0.5 
likemaxPauseTime = 6.5

class SINGLE_INSTANCE_MUTEX:
    """Windows Mutex를 사용하여 단일 인스턴스 실행을 보장하는 클래스"""

    def __init__(self, mutex_name):
        self.mutex_name = mutex_name
        self.mutex = None

    def already_running(self):
        self.mutex = ctypes.windll.kernel32.CreateMutexA(None, False, self.mutex_name)
        last_error = ctypes.windll.kernel32.GetLastError()
        return last_error == 183  # ERROR_ALREADY_EXISTS

# 메인 함수
def main():
    mutex_name = "Global\\MyApp12345Mutex"  # 고유한 이름 지정
    single_instance_mutex = SINGLE_INSTANCE_MUTEX(mutex_name)

    # 프로그램이 하나만 작동 되도록 확인
    if single_instance_mutex.already_running():
        print("프로그램이 이미 실행 중입니다. 프로그램을 종료합니다.")
        for i in range(3, 0, -1):
            print(i)
            time.sleep(1)
        sys.exit()

    global max_link_extract_cnt
    try:
        # OTP 인증
        secret_key = 'DIOFEPCKNMKOLEJFOSJOEHIUZHEBNKAL'
        if not validate_otp(secret_key):
            sys.exit()

        # 계정 및 기타 정보들 엑셀에서 가져오기
        account_datas = read_account_data_from_xlsx("accounts.xlsx")
        
        api_key, additional_comment, max_link_extract_cnt = \
            fetch_single_data_from_account_datas(account_datas)
        
        # 웹드라이버 초기화
        driver = initialize_driver()

        # openai 클라이언트 생성
        openai_client = OpenAIChatClient(api_key)

        # 자동화 처리
        for index, account_row in account_datas.iterrows():
            process_account(driver, account_row['id'], account_row['pw']
                            , account_row['닉네임']
                            , openai_client, additional_comment)
        
        print('===== ***** ===== ***** ===== ***** ===== ***** ===== *****')
        print('\n댓글 달기 및 좋아요 누르기 프로그램 실행이 모두 완료되었습니다.')
                
        driver.quit()

    except Exception as e:
        print(f"\n\n**** 프로그램 실행 오류 : {e}\n"
              "\n프로그램이 예기치 못하게 중단 되었습니다.")
        
    finally:
        if single_instance_mutex.mutex:
            ctypes.windll.kernel32.CloseHandle(single_instance_mutex.mutex)
        
            input("\n종료하려면 아무 키나 눌러주세요...")


# 계정마다 반복
def process_account(driver, id, pw, nickname, 
                    openai_client, additional_comment):
    
    # 로그인
    if not login_to_naver(driver, id, pw):
        print(f"\n계정 {id}의 로그인에 실패했습니다. 다음 계정으로 넘어갑니다.")
        return
    else :
        print(f"\n계정 {id}으로 로그인 하였습니다.")


    # 피드에서 블로그 링크 긁어오기
    link_list = get_blog_links(driver, max_link_extract_cnt)
    if link_list is None:
        return
    
    # 블로그 글 하나씩 반복
    comment_count = 0
    like_count = 0
    not_need_comment_count = 0
    not_need_like_count = 0
    for index, link in enumerate(link_list, start=1):
        
        # 진행상황 표시
        progress_percentage = (index / len(link_list)) * 100
        print('------------------------------------------------')
        print(f'{len(link_list)}개 중 {index}번째 링크 처리 중 ({progress_percentage:.1f}%):\n{link}')

        # 이미 댓글이 작성된 글인지 확인
        if is_already_commented(driver, link, nickname):
            print(f"\n'{id}'계정에 해당하는 댓글이 이미 존재합니다(닉네임-{nickname}). 다음 블로그 링크로 넘어갑니다.")
            not_need_comment_count += 1
            continue

        # 좋아요 처리
        like_count, not_need_like_count \
            = like_blog_post(driver, link, likeminPauseTime, likemaxPauseTime, 
                             like_count, not_need_like_count)
        
        # 글 내용 추출
        blog_content, error = extract_blog_content(driver)
        if error:
            print(error)
            continue
        
        # 작성자 이름 추출
        author_name = extract_author_name(driver)

        # AI를 통한 댓글 생성
        comment, error = generate_comment_with_ai(openai_client, blog_content, author_name, additional_comment)
        if error:
            print(error)
            continue
        
        # 댓글 등록
        if post_comment(driver, link, comment, index):
            comment_count += 1
        else:
            print(f'\n댓글 등록 실패 링크 : {link}. 다음 글로 넘어갑니다.')

    # 결과 출력
    print_final_output(id, len(link_list), not_need_comment_count, 
                       comment_count, like_count, not_need_like_count)
    
    # 로그아웃
    logout_of_naver(driver)

    

if __name__ == "__main__":
    main()
