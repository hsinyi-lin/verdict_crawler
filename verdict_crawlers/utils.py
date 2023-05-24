from datetime import date
import openai


def roc_to_ad(roc_date_str):
    roc_year, roc_month, roc_day = map(int, roc_date_str.split("."))
    ad_year = roc_year + 1911
    ad_date = date(ad_year, roc_month, roc_day)
    return ad_date


def call_openai(incident):
    openai.api_key = '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'

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "你是一個專門把內文產生適當的標題的助理."},
            {"role": "user", "content": incident}
        ]
    )

    return completion['choices'][0]['message']['content'].strip()