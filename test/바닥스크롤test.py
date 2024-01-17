
from selenium import webdriver
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from naver_utils import scroll_to_bottom

def test_scroll_to_bottom():
    # 크롬 드라이버 초기화
    driver = webdriver.Chrome()
    driver.get("https://m.blog.naver.com/SectionPostSearch.naver?orderType=sim&searchValue=%EA%B2%BD%EC%A0%9C")

    try:
        # 다음 매개변수를 실제 값으로 대체하세요
        link_selector = "a.link__OVpnJ"
        max_count = 300
        context = "테스트 컨텍스트"

        # 스크롤_아래로_함수를 테스트하기 위해 호출합니다.
        link_list = scroll_to_bottom(driver, link_selector, max_count, context)

        # link_list가 올바르게 채워졌는지 확인합니다.
        assert len(link_list) > 0, "스크롤_아래로_함수 테스트 실패"

        # 추출된 링크를 출력합니다.
        print("추출된 링크:")
        for link in link_list:
            print(link)
    except Exception as e:
        print(f"테스트 실패: {str(e)}")
    finally:
        driver.quit()

# test_scroll_to_bottom 함수 호출
test_scroll_to_bottom()
