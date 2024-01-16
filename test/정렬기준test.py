import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import blog_actions
from blog_actions import like_blog_post

def set_search_sorting(sorting_choice):
    """테스트용 정렬 방식 설정 함수"""
    sorting_preference = 'date' if sorting_choice == "1" else 'sim'
    return sorting_preference

def test_search_sorting():
    """블로그 검색 결과 정렬 방식 선택 테스트"""
    print("Testing search sorting selection...")

    # 테스트 케이스: 사용자 입력 모의
    test_inputs = ["1", "2", ""]
    expected_outputs = ["date", "sim", "date"]

    for i, input_value in enumerate(test_inputs):
        print(f"Test case {i+1}: Input = '{input_value}'")
        sorting_preference = set_search_sorting(input_value or "1")
        assert sorting_preference == expected_outputs[i], f"Failed: Expected {expected_outputs[i]}, got {sorting_preference}"
        print(f"Passed: {sorting_preference}")

# 테스트 실행
test_search_sorting()
