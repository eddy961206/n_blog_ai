import pyperclip
import random
import time
import traceback
import os
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, TimeoutException,
                                        ElementClickInterceptedException, UnexpectedAlertPresentException,
                                        NoAlertPresentException)
from bs4 import BeautifulSoup


def read_account_data_from_xlsx(excel_file):
    """엑셀에서 계정데이터 읽기"""
    try:
        df = pd.read_excel(excel_file)
        if not all(col in df.columns for col in ['id', 'pw', '닉네임', 'chatGPT api키']):
            raise ValueError("Excel 파일은 'id', 'pw', '닉네임', 'chatGPT api키' 열을 포함해야 합니다.")
        
        # 'id'와 'pw','닉네임' 컬럼에 유효한 데이터가 있는 행만 선택
        df = df[df['id'].notna() & df['pw'].notna() & df['닉네임'].notna()]

        # '댓글 뒤에 추가할 문구' 처리 (옵션)
        if '댓글 뒤에 추가할 문구' not in df.columns:
            df['댓글 뒤에 추가할 문구'] = ""
        else:
            df['댓글 뒤에 추가할 문구'] = df['댓글 뒤에 추가할 문구'].fillna('').astype(str)
        
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"\n\nExcel 파일을 찾을 수 없습니다: {excel_file}")
    except Exception as e:
        raise Exception(f"\n\nExcel 파일 {excel_file}을 읽는 중 오류가 발생했습니다: {e}")


def fetch_single_data_from_account_datas(account_datas):
    api_key = account_datas['chatGPT api키'].dropna().iloc[0]
    additional_comment = account_datas['댓글 뒤에 추가할 문구'].iloc[0] if not account_datas['댓글 뒤에 추가할 문구'].isnull().all() else ""
    
    return api_key, additional_comment


def initialize_driver():
    """크롬 드라이버 초기화"""
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    return driver


def get_feed_blog_count():
    """사용자로부터 피드 개수 입력받기"""
    feed_blog_input = input("\n서로이웃의 피드에서 작업할 블로그 글 개수를 입력해주세요\n(빈 값 입력시 피드에서 작업 생략): ")
    return int(feed_blog_input) if feed_blog_input.isdigit() else 0


def get_keyword_and_count():
    """사용자로부터 키워드, 키워드 검색 개수 입력받기"""
    keyword = input("\n키워드를 통한 블로그 검색 작업 시 사용할 키워드를 입력해주세요\n(빈 값 입력시 키워드 검색 생략): ")
    if keyword:
        keyword_blog_input = input("\n키워드 검색에서 작업할 블로그 글 개수를 입력해주세요\n(빈 값 입력시 키워드 검색 생략): ")
        keyword_blog_count = int(keyword_blog_input) if keyword_blog_input.isdigit() else 0

        if keyword_blog_count > 0:
            print("\n블로그 검색 결과 정렬 방식을 숫자로 선택해주세요:\n 1: 최신순 (기본값)\n 2: 정확도순\n(빈 값 입력시 최신순으로 자동 선택)")
            sorting_choice = input() or "1"
            sorting_preference = 'date' if sorting_choice != "2" else 'sim'
        else:
            sorting_preference = None
    else:
        keyword_blog_count = 0
        sorting_preference = None

    return keyword, keyword_blog_count, sorting_preference
   

def login_to_naver(driver, username, password):
    driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com")
    try:
        driver.find_element(By.CSS_SELECTOR, "#id").click()
        time.sleep(0.5)
        pyperclip.copy(username)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        
        driver.find_element(By.CSS_SELECTOR, "#pw").click()
        time.sleep(0.5)
        pyperclip.copy(password)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        
        driver.find_element(By.CSS_SELECTOR, "#log\\.login").click()
        time.sleep(3)
        
        return True
    except NoSuchElementException:
        print("\n\n로그인 버튼을 찾을 수 없습니다.")
        return False
    except TimeoutException:
        print("\n\n로그인 페이지가 로드되는데 시간이 너무 오래 걸립니다.")
        return False
    except Exception as e:
        print(f"\n\n로그인 시도중 오류 발생 : {e}")
        return False


def set_search_sorting(driver, sorting_preference):
    """블로그 검색 결과 페이지에서 정렬 방식 설정"""
    try:
        sort_select = Select(driver.find_element(By.CSS_SELECTOR, "select.select__IkE09"))
        sort_select.select_by_value(sorting_preference)
    except Exception as e:
        print(f"블로그 검색결과 정렬 방식 설정 중 오류 발생: {e}")


def get_feed_blog_links(driver, max_count):
    """블로그 피드 링크 추출"""
    feed_url = "https://m.blog.naver.com/FeedList.naver"
    link_selector = "a.link__iGhdI"
    context = "서로이웃 피드"
    return fetch_blog_links(driver, feed_url, link_selector, max_count, context)


def search_blog_by_keyword(driver, keyword, max_count, sorting_preference):
    """키워드로 블로그 검색하고 링크 추출"""
    search_url = f"https://m.blog.naver.com/SectionPostSearch.naver?orderType=sim&searchValue={keyword}"
    link_selector = "a.link__OVpnJ"
    context = "키워드 검색 결과"
    return fetch_blog_links(driver, search_url, link_selector, max_count, context, sorting_preference)


def fetch_blog_links(driver, url, link_selector, max_count, context, sorting_preference=None):
    """공통 링크 추출 함수"""
    try:
        driver.get(url)

        time.sleep(2)
        # 키워드로 블로그 검색할 때만 정렬순서 세팅
        if sorting_preference:
            set_search_sorting(driver, sorting_preference)

        time.sleep(2)
    except Exception as e:
        print(f"{context} 링크 추출 페이지로 이동하는데 실패했습니다: {e}")
        return None

    link_list = scroll_to_bottom(driver, link_selector, max_count, context)

    if len(link_list) < max_count:
        print(f"{context}에서 충분한 수의 링크를 찾지 못했습니다.")

    return link_list


def navigate_to_comment_page(driver, link):
    """블로그 글의 댓글 페이지로 이동"""
    try:
        # URL을 분해하여 댓글 페이지의 링크 생성
        url_parts = link.split('&')  # https://m.blog.naver.com/PostView.naver?blogId=u_many_yeon&logNo=223316337997&navType=by -> https://m.blog.naver.com/CommentList.naver?blogId=u_many_yeon&logNo=223316337997
        comment_page_link = link.replace("PostView.naver", "CommentList.naver").split('&')[0] + '&' + url_parts[1]
        driver.get(comment_page_link)
        
        return True
    except Exception as e:
        print(f"댓글 페이지로 이동하는 도중 오류가 발생했습니다: {e}")
        return False


def is_already_commented(driver, link, nickname):
    """특정 닉네임의 존재 여부 확인(댓글 이미 달았는지)"""
    try:
        # 댓글 페이지로 이동
        navigate_to_comment_page(driver, link)

        #### TDOO : 1.5초가 아니라 로딩다 되면 바로 위로 스크롤 될 수 있게 바꿔야
        time.sleep(1.5)

        # 스크롤을 맨 위로 이동
        scroll_to_top(driver)     

        # 닉네임이 페이지에 존재하는지 확인
        return bool(driver.find_element(By.XPATH, f"//span[@class='u_cbox_nick' and contains(text(), '{nickname}')]"))

    except UnexpectedAlertPresentException:
        # 댓글 페이지에서 경고창이 나타나면 처리
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            raise CommentNotAllowedException(f"댓글을 달 수 없는 블로그 글입니다: {alert_text}")
        except NoAlertPresentException:
            print("경고창을 처리하는 중 오류 발생")
        return False
    except NoSuchElementException:
        # 닉네임 요소 자체가 페이지에 없으면 False 반환
        return False
    except Exception as e:
        print(f"이미 댓글 단 블로그인지 확인하는 도중 에러 발생 : {str(e)}")
        return False

def scroll_to_top(driver):
    """브라우저 스크롤을 맨 위로 이동하고 새로운 컨텐츠 로드될 때까지 반복"""
    while True:
        # 현재 스크롤 위치 저장
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
        
        # 스크롤을 맨 위로 이동
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)  # 짧은 대기 시간

        # 새로운 스크롤 위치 확인
        new_scroll_position = driver.execute_script("return window.pageYOffset;")

        # 스크롤 위치가 변하지 않았다면 중단
        if current_scroll_position == new_scroll_position:
            break        


def like_blog_post(driver, link, likeminPauseTime, likemaxPauseTime, like_count, not_need_like_count):
    """좋아요 클릭"""
    driver.get(link)  # 블로그 본문 페이지로 이동

#   #### 클라이언트의 요청. 체류시간 상관 없어하심. 체류시간 중요하지만 #####
    # time.sleep(1)
    # scroll_through_post(driver, likeminPauseTime, likemaxPauseTime)
#   #### 클라이언트의 요청. 체류시간 상관 없어하심. 체류시간 중요하지만 #####

    try:
        heart_btn_selector = "a.u_likeit_list_btn._button._sympathyBtn"
        # 좋아요 버튼이 있는지 먼저 확인
        if driver.find_elements(By.CSS_SELECTOR, heart_btn_selector):
            heart_btn = find_element_with_retry(driver, By.CSS_SELECTOR, heart_btn_selector)
            if heart_btn and heart_btn.get_attribute("aria-pressed") == "false":
                driver.execute_script("arguments[0].click();", heart_btn)
                time.sleep(1.5)
                like_count = handle_alert(driver, like_count)
            else:
                print('\n이미 좋아요가 눌려있습니다.')
                not_need_like_count += 1
        else:
            print("\n좋아요 할 수 없는 블로그 글입니다.")
    except UnexpectedAlertPresentException as e:
        print(f'\n좋아요 클릭 중 오류 발생: {str(e)}')

    return like_count, not_need_like_count


def handle_alert(driver, like_count):
    """좋아요 버튼 예외시 alert 확인 처리"""
    try:
        alert = driver.switch_to.alert
        alert.accept()
        print("\n해당 컨텐츠에 더 이상 좋아요 할 수 없습니다.")
    except NoAlertPresentException:
        like_count += 1
        print("\n좋아요 눌림")
    
    return like_count


def find_element_with_retry(driver, by, value, delay=5):
    """요소가 나타날 때까지 찾기"""
    try:
        element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        # 요소가 지정된 시간 내에 나타나지 않으면 None 반환하거나 예외 발생
        return None
        # 또는 필요에 따라 예외를 발생시킬 수 있습니다:
        # raise NoSuchElementException(f"요소가 {delay}초 동안 나타나지 않았습니다: {value}")


#### TODO : 스크롤 아래로 내려갈수록 링크가 누적되서 점점 실행속도가 느려지는 것 보완해야
def scroll_to_bottom(driver, link_selector, max_count, context):
    """페이지 끝까지 스크롤하며 링크 수집"""
    link_list = []
    wait = WebDriverWait(driver, 10)  # 최대 10초 동안 기다림

    while True:
        current_links = driver.find_elements(By.CSS_SELECTOR, link_selector)
        new_links = [link.get_attribute("href") for link in current_links if link.get_attribute("href") not in link_list]

        if not new_links:
            break  # 새로운 링크가 없으면 중단

        link_list.extend(new_links)  # 새로운 링크 추가

        # 지정한 최대 개수에 도달하면 초과된 링크 제거
        if len(link_list) > max_count:
            link_list = link_list[:max_count]
            print(f"\n{context}에서 지정한 최대 글 수 {max_count}개에 도달했습니다.")
            break

        # 페이지 끝으로 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 새로운 콘텐츠가 로드될 때까지 기다림
        try:
            wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR,link_selector)) > len(current_links))
        except TimeoutException:
            break # 새 콘텐츠 로드 실패 시 중단

    # 링크가 충분하지 않으면 메시지 출력
    if len(link_list) < max_count:
        print(f"{context}에서 충분한 수의 링크를 찾지 못했습니다.")

    return link_list

def scroll_through_post(driver, likeminPauseTime, likemaxPauseTime):
    """포스트 글 안에서 천천히 스크롤(체류시간 중요함)"""
    document_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.find_element(By.XPATH, "//body").send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(likeminPauseTime, likemaxPauseTime))
        now_scroll_height = driver.execute_script("return window.scrollY + window.innerHeight")
        if now_scroll_height >= document_height:
            break
        document_height = driver.execute_script("return document.body.scrollHeight")
    

def extract_blog_content(driver):
    """Extract the blog content from a blog post."""
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    blog_content_div = soup.find("div", class_="se-main-container")
    if not blog_content_div:
        return None, "\n블로그 본문을 찾을 수 없습니다.\n다음 글로 넘어갑니다."
    
    blog_content = ''
    for element in blog_content_div.descendants:
        if element.name == 'span':
            if element.string:
                blog_content += element.string.strip() + ' '
    
    if not blog_content:
        return None, "\n블로그 본문 내용이 비어있습니다.\n다음 글로 넘어갑니다."
    
    print(f'\n본문 글 : \n{blog_content}')
    
    return blog_content, None


def extract_author_name(driver):
    """Extract the author's nickname from the blog post."""
    try:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        author_div = soup.find("div", class_="blog_author")
        if author_div and author_div.find("strong", class_="ell"):
            author_name = author_div.find("strong", class_="ell").get_text().strip()
        else:
            author_name = " "
    except Exception as e:
        print(f'\n작성자 닉네임 추출중 오류 발생: {str(e)}')
        author_name = " "

    print("\n작성자 : ", author_name)

    return author_name


def generate_comment_with_ai(openai_client, blog_content, author_name, additional_comment):
    """Generate a comment for a blog post using OpenAI."""
    try:
        comment = openai_client.generate_comment(blog_content, author_name, additional_comment)

        print(f"\n생성된 댓글 : \n{comment}")

        return comment, None
    except Exception as e:
        return None, f'댓글 생성 중 오류 발생: {str(e)}\n 다음 글로 넘어갑니다..'


def post_comment(driver, link, comment, index):
    """Post a comment on a blog post and return True if successful."""
    try:
        if not navigate_to_comment_page(driver, link):
            return False
        
        comment_box = find_element_with_retry(driver, By.CSS_SELECTOR, "#naverComment__write_textarea")
        
        driver.execute_script("""
            var commentDiv = arguments[0];
            commentDiv.innerText = arguments[1];
        """, comment_box, comment)

        submit_button = find_element_with_retry(driver, By.CSS_SELECTOR, ".u_cbox_btn_upload")
        time.sleep(0.5)
        submit_button.click()
        print(f'\n\n{index}번째 블로그 글에 댓글 등록이 완료됐습니다.')
        print('--------------------------------------')

        return True
    except Exception as e:
        print(f'\n\n{index}번째 블로그 글에 댓글 등록이 실패했습니다 : {e}')
        traceback.print_exc()
        return False


def logout_of_naver(driver):
    """Logs out of Naver."""
    try:
        driver.get("https://www.naver.com/")
        logout_button = find_element_with_retry(driver, By.CSS_SELECTOR, ".MyView-module__btn_logout___bsTOJ")
        time.sleep(0.3)
        logout_button.click()
    except NoSuchElementException:
        print("로그아웃 버튼을 찾을 수 없습니다.")
    except ElementClickInterceptedException:
        print("로그아웃 버튼을 클릭할 수 없습니다.")

def print_final_output(naver_id, link_list_total, not_need_comment_count, 
                       comment_count, like_count, not_need_like_count):
    # 좋아요 눌러야 할 블로그 수
    need_like_count = link_list_total - not_need_like_count

    # 좋아요 완수율 계산
    if need_like_count > 0:
        like_completion_rate = (like_count / need_like_count) * 100
    else:
        like_completion_rate = 0

    # 댓글 달아야 할 블로그 수
    need_comment_count = link_list_total - not_need_comment_count

    # 댓글 달기 완수율 계산
    if need_comment_count > 0:
        comment_completion_rate = (comment_count / need_comment_count) * 100
    else:
        comment_completion_rate = 0

    # 좋아요 완수율 계산
    if need_comment_count > 0:
        like_completion_rate = (like_count / need_comment_count) * 100
    else:
        like_completion_rate = 0

    # 결과 출력
    print('------------------------------------------------')
    print(f'\n\n{naver_id} 계정으로 블로그 댓글 달기가 완료되었습니다.\n\n'
        f'피드에서 긁어온 블로그 : {link_list_total}개\n'
        f'댓글이 안 달려있던 블로그 : {need_comment_count}개\n'
        f'좋아요가 안 달려있던 블로그 : {need_like_count}개\n\n'
        f'작성한 댓글 : {comment_count}개\n'
        f'좋아요 : {like_count}개\n')
    print(f'- 댓글 달기 완수율 : {comment_completion_rate:.1f}%')
    print(f'- 좋아요 완수율    : {like_completion_rate:.1f}%')
    print('------------------------------------------------')


class CommentNotAllowedException(Exception):
    """예외 클래스: 댓글을 달 수 없는 블로그 글을 나타냄"""
    def __init__(self, message="댓글을 달 수 없는 블로그 글입니다. 다음 블로그 링크로 넘어갑니다."):
        self.message = message
        super().__init__(self.message)