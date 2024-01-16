import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import blog_actions
from blog_actions import like_blog_post
from blog_actions import scroll_to_top, navigate_to_comment_page, is_already_commented
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException


# 웹 드라이버 초기화 (Chrome을 사용하도록 설정)
driver = webdriver.Chrome()

# 테스트를 위한 블로그 글 링크와 닉네임 설정 (실제로 사용하실 링크와 닉네임으로 변경)
blog_link = "https://m.blog.naver.com/PostView.naver?blogId=mentalisia&logNo=223308203874&navType=by"
# blog_link = "https://m.blog.naver.com/PostView.naver?blogId=sosimrun&logNo=223324492952&searchKeyword=%EA%B2%BD%EC%A0%9C%EC%A0%81%20%EC%9E%90%EC%9C%A0"
# blog_link = "https://m.blog.naver.com/PostView.naver?blogId=bluerose0328&logNo=223324522433&searchKeyword=%EB%8F%88"


nickname = "호주수즈sujbites"  # 테스트할 닉네임으로 변경
# nickname = "Liverpool"  # 테스트할 닉네임으로 변경

# navigate_to_comment_page 함수 테스트
def test_navigate_to_comment_page():
    try:
        result = navigate_to_comment_page(driver, blog_link)
        assert result, "navigate_to_comment_page 함수 테스트 실패"
        print("navigate_to_comment_page 함수 테스트 성공")
    except Exception as e:
        print(f"navigate_to_comment_page 함수 테스트 실패: {str(e)}")

# scroll_to_top 함수 테스트
def test_scroll_to_top():
    try:
        result = scroll_to_top(driver)
        assert result, "scroll_to_top 함수 테스트 실패"
        print("scroll_to_top 함수 테스트 성공") 
    except Exception as e:
        print(f"scroll_to_top 함수 테스트 실패: {str(e)}")

# is_already_commented 함수 테스트
def test_is_already_commented():
    try:
        result = is_already_commented(driver, blog_link, nickname)
        print(f"{nickname} 찾았나? : {result}")
        assert result, "is_already_commented 함수 테스트 실패"
        print("is_already_commented 함수 테스트 성공")
        input()
    except Exception as e:
        print(f"is_already_commented 함수 테스트 실패: {str(e)}")
        input()

# 테스트 실행
try:
    test_navigate_to_comment_page()
    test_scroll_to_top()
    test_is_already_commented()
except Exception as e:
    print(f"테스트 실패: {str(e)}")

# 웹 드라이버 종료
driver.quit()

