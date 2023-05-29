from datetime import date
import openai

openai.api_key = ''


def roc_to_ad(roc_date_str):
    roc_year, roc_month, roc_day = map(int, roc_date_str.split("."))
    ad_year = roc_year + 1911
    ad_date = date(ad_year, roc_month, roc_day)
    return ad_date


def call_openai_title(incident):
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "你是一個專門把犯罪過程產生標題並轉成繁體中文的助理"},
            {"role": "user", "content": incident}
        ]
    )
    return completion['choices'][0]['message']['content'].strip()


def call_openai_incident_lite(incident):
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "你是一個專門把犯罪過程內容轉成口語化內容並繁體中文摘要的助理，只要回傳轉換後的內容結果就好，回傳的內容不能超過250字"},
            {"role": "user", "content": incident}
        ]
    )
    return completion['choices'][0]['message']['content'].strip()


# def call_openai(incident):
#     openai.api_key = ''

#     response = openai.Completion.create(
#         model="text-davinci-003",
#         prompt=f"產生45個字以內標題：{incident}",
#         temperature=0,
#         max_tokens=60,
#         top_p=1,
#         frequency_penalty=0.5,
#         presence_penalty=0
#     )

#     return response['choices'][0]['text'].strip()
