from selenium import webdriver
from selenium.webdriver.common.by import By
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from naver_utils import login_to_naver, post_comment
import time
from selenium.webdriver.common.keys import Keys

from program_actions import initialize_driver
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC




# def post_comment(driver, comment):
#     try:
#         wait = WebDriverWait(driver, 10)
#         comment_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#naverComment__write_textarea")))

#         comment_box.clear()  # 기존 내용을 지우고
#         comment_box.send_keys(comment)  # 새로운 댓글을 입력합니다.

#         # Enter 키를 눌러서 댓글을 제출할 수 있습니다.
#         comment_box.send_keys(Keys.RETURN)
        
#         print("댓글 입력 완료")
#         input()

#         return True
#     except Exception as e:
#         print(f"댓글 입력 실패: {e}")
#         input()

#         return False

# 테스트할 웹페이지 URL 설정 (예: Naver 블로그의 특정 게시글)

driver = initialize_driver()

login_to_naver(driver, "sykum20212", "fbtmdxor96!")

url = "https://m.blog.naver.com/CommentList.naver?blogId=zcx9832&logNo=223330140594"
# 웹 페이지 열기
driver.get(url)

# 테스트용 댓글 내용
test_comment = "좋은 글이네요! \n\n잘 보았습니다."

# 댓글 작성 테스트 실행
post_comment(driver, url, test_comment, 1)
input()
# 테스트 후 정리
time.sleep(5)  # 결과 확인을 위한 대기 시간
driver.quit()
