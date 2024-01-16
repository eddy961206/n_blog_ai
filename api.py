from openai import OpenAI, APIError

class OpenAIChatClient:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_comment(self, blog_content, author_name, additional_comment):

        try:
            instruction = f"""
You're a blog commenting expert. Please follow the instructions below to create a comment on a blog post.

1. Read the blog content carefully and understand exactly what the author is trying to say.
2. Write a 2-3 line comment using at least 1 important keyword from the post in a nuanced way that resonates with the topic and the author.
3. If the author name (author_name) is given, mention '{author_name}님' at least once to create a sense of familiarity.  
4. If author name is not given, do not mention the author at all, just talk about the content.
5. Make it as natural as possible, like a human wrote it, not a machine.
6. Use a bit more colloquial language while keeping it natural.
7. Only write a comment in natural Korean so that it can be copied and used directly.
8. Never say anything negative, never use 반말, never say '당신'.
9. Use formal speech and honorifics.
10. Never misspell the author's name.
"""
   
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": blog_content}
                ]
            )
            # print('첫 리스폰스 : ', response)
            response_message = response.choices[0].message.content

            if additional_comment:
                response_message += f"\n\n{additional_comment}"

            return response_message
        
        except APIError as e:
            print(f"CHATGPT API 호출 중 오류가 발생했습니다: {e}\n다음 글로 넘어갑니다.")
            return None
        
        except Exception as e:
            print(f"CHATGPT API 호출 중 예상치 못한 오류가 발생했습니다: {e}\n다음 글로 넘어갑니다.")
            return None
        
