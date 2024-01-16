import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import blog_actions
from blog_actions import like_blog_post

# 웹 드라이버 초기화 (Chrome을 사용하도록 설정)
driver = webdriver.Chrome()

# 테스트를 위한 블로그 글 링크 설정 (실제로 사용하실 링크로 변경)
blog_link = "https://m.blog.naver.com/PostView.naver?blogId=sosimrun&logNo=223324492952&searchKeyword=%EA%B2%BD%EC%A0%9C%EC%A0%81%20%EC%9E%90%EC%9C%A0"  # 대상 블로그 글 링크로 변경

# like_blog_post 함수 테스트
def test_like_blog_post():
    try:
        like_count = 0
        not_need_like_count = 0


        like_count, not_need_like_count = like_blog_post(driver, blog_link, 1, 3, like_count, not_need_like_count)

        print(f"좋아요 클릭 횟수: {like_count}")
        print(f"이미 좋아요가 눌려있어서 클릭하지 않은 횟수: {not_need_like_count}")
        input()
    except Exception as e:
        print(f"좋아요 클릭 함수 테스트 실패: {str(e)}")
        input()
# 테스트 함수 실행
test_like_blog_post()

# 웹 드라이버 종료
driver.quit()
