from program_actions import (read_account_data_from_xlsx, initialize_driver, get_feed_blog_count,
                          get_keyword_and_count,fetch_single_data_from_account_datas, print_final_output)
from naver_utils import (login_to_naver, get_feed_blog_links, search_blog_by_keyword, is_already_commented,
                          CommentNotAllowedException, like_blog_post, extract_blog_content, 
                          extract_author_name, generate_comment_with_ai, post_comment, 
                          logout_of_naver)
from api import OpenAIChatClient

likeminPauseTime = 0.5 
likemaxPauseTime = 6.5

# 메인 로직 함수
def main_logic(api_key, additional_comment, 
               account_infos, feed_blog_count, keyword, 
               keyword_blog_count, sorting_preference):
    
    try:
            
        print('\n\n===============  프로그램 작동중.... ===============')
        print('\n\n=== 화면은 가려져도 되지만 크롬 창 최소화는 하지 말아주세요 ===')

        # 웹드라이버 초기화
        driver = initialize_driver()


        # openai 클라이언트 생성
        openai_client = OpenAIChatClient(api_key)

        # 자동화 처리
        for account_info in account_infos:
            login_id, password, nickname = account_info.split(", ")
            process_account(driver, login_id, password, nickname, 
                            openai_client, additional_comment,
                            feed_blog_count, keyword, 
                            keyword_blog_count, sorting_preference)
        
        print('===== ***** ===== *****  ===== ***** ===== *****')
        print('\n댓글 달기 및 좋아요 누르기 프로그램 실행이 모두 완료되었습니다.')
                
        driver.quit()

    except Exception as e:
        print(f"\n\n**** 프로그램 실행 오류 : {e}\n"
              "\n프로그램이 예기치 못하게 중단 되었습니다.")


# 계정마다 반복
def process_account(driver, id, pw, nickname, openai_client, additional_comment,
                    feed_blog_count, keyword, keyword_blog_count, sorting_preference):
    
    # 로그인
    if not login_to_naver(driver, id, pw):
        print(f"\n계정 {id}으로 로그인에 실패했습니다. 다음 계정으로 넘어갑니다.")
        return
    else :
        print(f"\n계정 {id}으로 로그인 하였습니다.")


    # 피드에서 블로그 링크 가져오기
    feed_links = []
    if feed_blog_count > 0:
        feed_links = get_feed_blog_links(driver, feed_blog_count)
        if feed_links is None:
            print("피드에 블로그 글이 존재하지 않습니다.")

    print(f"피드 링크 개수: {len(feed_links)}")
    
    # 키워드 검색으로 블로그 링크 가져오기
    keyword_links = []
    if keyword and keyword_blog_count > 0:
        keyword_links = search_blog_by_keyword(driver, keyword, keyword_blog_count, sorting_preference)
        if keyword_links is None:
            print("키워드 검색 결과에 블로그 글이 존재하지 않습니다.")

    print(f"키워드 링크 개수: {len(keyword_links)}")
    
    # 가져온 링크들 중복 제거 및 합치기
    link_list = list(set(feed_links + keyword_links))
    print(f"\n총 좋아요와 댓글을 달 블로그 글 개수(중복제외) : {len(link_list)}개")

    ##########################################################
    # 블로그 글 하나씩 반복  
    comment_count = 0
    like_count = 0
    not_need_comment_count = 0
    not_need_like_count = 0
    
    for index, link in enumerate(link_list, start=1):
        
        # 진행상황 표시
        progress_percentage = (index / len(link_list)) * 100
        print('\n------------------------------------------------')
        print(f'{len(link_list)}개 중 {index}번째 링크 처리 중 ({progress_percentage:.1f}%):\n{link}')

        # 이미 댓글이 작성된 글인지 확인
        try:
            if is_already_commented(driver, link, nickname):
                print(f"\n'{id}'계정에 해당하는 댓글이 이미 존재합니다(닉네임-{nickname}). 다음 블로그 링크로 넘어갑니다.")
                not_need_comment_count += 1
                continue
        except CommentNotAllowedException as e:
            print(e)
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


