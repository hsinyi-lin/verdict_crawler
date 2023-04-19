from datetime import date
import openai


def roc_to_ad(roc_date_str):
    roc_year, roc_month, roc_day = map(int, roc_date_str.split("."))
    ad_year = roc_year + 1911
    ad_date = date(ad_year, roc_month, roc_day)
    return ad_date


def call_openai(incident):
    openai.api_key = ''

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"產生45個字以內標題：{incident}",
        temperature=0,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0
    )

    return response['choices'][0]['text'].strip()