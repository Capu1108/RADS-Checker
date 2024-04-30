from openai import OpenAI
import httpx
import pandas as pd

#
proxy_url = "http://127.0.0.1:7890"

#
httpx_client = httpx.Client(proxies={"http://": proxy_url, "https://": proxy_url})
client = OpenAI(
    api_key="",#OpenAI's API
    http_client=httpx_client
)

template = '''
Answer two questions based on the privacy policy text provided at the end. In addition, each of the rights mentioned in the question has its own implementation methods, which we group into three categories: email contact, account settings, and webform submissions.
Please format your answers in JSON, such as: {"al": {"Right" : "0", "Methods" : "0"}, " a2" :{"Right" : "1", "Methods" : "1,2"7}.
"al" and "a2" are the responses to the first and second questions, respectively. "Right" indicates whether there's a corresponding right declaration, with "I" meaning yes and "0" meaning no.
"Methods" represents the implementation methods associated with the right, where "1" "2" and
"3" represent email contact, account settings, and webform submission, respectively.
Questions:
"""
Is there the right provided for users to obtain a copy of their personal data?
Is there the right provided for users to access their personal data?
"""
Privacy Policy Text:
"""
{content}
"""
'''

def chatWithGPT(file_path):
    # 读取csv文件
    df = pd.read_csv(file_path)
    for part in df['paragraph']:
        if part.strip():  # 检查分段是否为空
            prompt = template.replace('{content}', part)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional analyst specializing in GDPR and privacy policy compliance. Review the privacy policy provided to address specific user rights and their implementation methods."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            out = completion.choices[0].message.content
            print(out)
if __name__=="__main__":
    chatWithGPT('data/test.csv')








