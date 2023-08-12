from datetime import date
import openai, time

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
            {"role": "system", "content": "你是一個專門把犯罪過程產生10字標題並轉成繁體中文的助理"},
            {"role": "user", "content": incident}
        ]
    )

    time.sleep(25)
    return completion['choices'][0]['message']['content'].strip()


def call_openai_incident_lite(incident):
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "你是一個專門把犯罪過程內容轉成口語化內容並繁體中文摘要的助理，只要回傳轉換後的內容結果就好，回傳的內容不能超過150字"},
            {"role": "user", "content": incident}
        ]
    )
    time.sleep(25)
    return completion['choices'][0]['message']['content'].strip()


def call_openai_find_features(incident):
    content = '呂文進前因竊盜案件，經臺灣新竹地方法院以110年度竹簡字第214號判決處有期徒刑2月確定，與前案竊盜案件經同法院裁定定應執行有期徒刑5月確定，於民國111年1月30日徒刑執畢出監。猶不知悔改，意圖為自己不法所有，基於竊盜之犯意，於111年6月22日17時50分許，在臺北市○○區○○街000號前，徒手竊取陳明楠置於該處之腳踏車1輛【價值新臺幣（下同）1,500元】後，隨即將腳踏車牽離現場而得手(已發還)。嗣經陳明楠察覺遺失而報警處理，經警循線調閱監視器影像，始查悉上情。'
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一個根據犯罪過程專門負責回答使用者一連串問題並且依序題目只會回答是或否的助理，並且每個問題都用頓號(、)來區隔的助理"},
            {"role": "user", "content": f'{content}，犯罪人偷竊物是否為金錢相關、是否有遺棄贓物、是否犯罪地點為室內、是否竊盜方法具破壞性、是否為兩人以上(含)犯案、是否使用交通工具來輸送贓物、是否有前科紀錄、是否竊取之財物為被害人生財工具'},
            {"role": "assistant", "content": '否、否、否、否、否、否、是、否、否'},
            {"role": "user", "content": f'{incident}，犯罪人偷竊物是否為金錢相關、是否有遺棄贓物、是否犯罪地點為室內、是否竊盜方法具破壞性、是否為兩人以上(含)犯案、是否使用交通工具來輸送贓物、是否有前科紀錄、是否竊取之財物為被害人生財工具'},
        ]
    )

    # 竊盜
    # item['is_money_related'], item['is_abandoned'], item['is_indoor'], item['is_destructive'], \
    #     item['is_group_crime'], item['is_transportation_used'], item['has_criminal_record'], \
    #         item['is_income_tool'] = data['features']

    response_message = completion['choices'][0]['message']['content'].strip()
    clean_list = response_message.split('、')

    if len(clean_list) != 8:
        print(False)
        return False

    clean = []
    for item in clean_list:
        if '否' in item or '不是' in item:
            clean.append(False)
        else:
            clean.append(True)

    time.sleep(25)
    print(clean)
    return clean


def call_openai_prison_term(result):
    content = ['林晁玄犯竊盜罪，處有期徒刑貳月，如易科罰金，以新臺幣壹仟元折算壹日。',  '梁佑全犯竊盜罪，處有期徒刑肆月，如易科罰金，以新臺幣壹仟元折算壹日。']

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一個根據判決結果回答出有期徒刑幾個月，並且只用阿拉伯數字回答的助理"},
            {"role": "user", "content": f'{content[0]}，根據內容，有期徒刑幾個月'},
            {"role": "assistant", "content": '2'},
            {"role": "user", "content": f'{content[1]}，根據內容，有期徒刑幾個月'},
            {"role": "assistant", "content": '4'},
            {"role": "user", "content": f'{result}，根據內容，有期徒刑幾個月'},
        ]
    )

    response_message = completion['choices'][0]['message']['content'].strip()
    
    try:
        month = int(response_message)
    except:
        return False
    
    time.sleep(25)
    print(month)
    return month