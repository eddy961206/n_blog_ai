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
from selenium.webdriver.support.ui import WebDriverWait
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

        # '댓글 달 최대 블로그 개수' 처리 (옵션, 기본값 100)
        if '댓글 달 최대 블로그 개수' not in df.columns or df['댓글 달 최대 블로그 개수'].isnull().all():
            df['댓글 달 최대 블로그 개수'] = 100
        else:
            df['댓글 달 최대 블로그 개수'].fillna(100, inplace=True)
        
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"\n\nExcel 파일을 찾을 수 없습니다: {excel_file}")
    except Exception as e:
        raise Exception(f"\n\nExcel 파일 {excel_file}을 읽는 중 오류가 발생했습니다: {e}")


def fetch_single_data_from_account_datas(account_datas):
    api_key = account_datas['chatGPT api키'].dropna().iloc[0]
    additional_comment = account_datas['댓글 뒤에 추가할 문구'].iloc[0] if not account_datas['댓글 뒤에 추가할 문구'].isnull().all() else ""
    max_link_extract_cnt = int(account_datas['댓글 달 최대 블로그 개수'].iloc[0]) if not account_datas['댓글 달 최대 블로그 개수'].isnull().all() else 100

    return api_key, additional_comment, max_link_extract_cnt


def initialize_driver():
    """크롬 드라이버 초기화"""
    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    return driver


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


def get_blog_links(driver, max_link_extract_cnt):
    """블로그 링크 추출"""
    try:
        driver.get("https://m.blog.naver.com/FeedList.naver")
        time.sleep(3)
    except Exception as e:
        print(f"블로그 피드 페이지로 이동하는데 실패했습니다: {e}")
        return None

    link_selector = "a.link__iGhdI"
    link_list = []
    while len(link_list) < max_link_extract_cnt:
        if not scroll_to_bottom(driver):
            print("블로그 피드 페이지 스크롤 끝에 도달했습니다. 더 이상 컨텐츠가 없습니다.")
            break  

        time.sleep(1)
        link_elements = driver.find_elements(By.CSS_SELECTOR, link_selector)
        for link_element in link_elements:
            link_href = link_element.get_attribute("href")
            if link_href not in link_list:
                link_list.append(link_href)
            if len(link_list) == max_link_extract_cnt:
                print(f"\n\n블로그 피드 스크래핑 중 지정한 최대 댓글 작성 수 {max_link_extract_cnt}개에 도달했습니다.")
                break

    if not link_list:
        print("피드에 블로그 글이 없습니다.")
        return None

    print('\n읽어들인 블로그 링크 갯수 : ', len(link_list))
    print('\n================================================\n'
          '================================================\n')

    return link_list[:max_link_extract_cnt]


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
        time.sleep(1)

        # 닉네임이 페이지에 존재하는지 확인
        return bool(driver.find_element(By.XPATH, f"//span[@class='u_cbox_nick' and contains(text(), '{nickname}')]"))
    except NoSuchElementException:
        # 닉네임이 페이지에 없으면 False 반환
        return False
    except Exception as e:
        print(f"이미 댓글 단 블로그인지 확인하는 도중 에러 발생 : {e}")


def like_blog_post(driver, link, likeminPauseTime, likemaxPauseTime, like_count, not_need_like_count):
    """좋아요 클릭"""
    driver.get(link)  # 블로그 본문 페이지로 이동
    scroll_through_post(driver, likeminPauseTime, likemaxPauseTime)
    try:
        heart_btn_selector = "a.u_likeit_list_btn._button._sympathyBtn"
        heart_btn = find_element_with_retry(driver, By.CSS_SELECTOR, heart_btn_selector)
        if heart_btn.get_attribute("aria-pressed") == "false":
            driver.execute_script("arguments[0].click();", heart_btn)
            time.sleep(1)
            like_count = handle_alert(driver, like_count)
        else:
            print('\n이미 좋아요가 눌려있습니다.')
            not_need_like_count += 1
    except NoSuchElementException:
        print("\n좋아요 버튼을 찾을 수 없습니다.")
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


def find_element_with_retry(driver, by, value, delay=10):
    """요소가 나타날 때까지 찾기"""
    element = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((by, value))
    )
    return element


def scroll_to_bottom(driver):
    """바닥까지 마우스 스크롤"""
    old_position = driver.execute_script("return window.pageYOffset;")
    driver.execute_script("window.scrollBy(0, 10000);")
    time.sleep(random.uniform(1, 3))
    new_position = driver.execute_script("return window.pageYOffset;")
    return new_position != old_position


def scroll_through_post(driver, likeminPauseTime, likemaxPauseTime):
    """포스트 글 안에서 천천히 스크롤"""
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
        return None, f'댓글 생성 중 오류 발생: {str(e)}'


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
