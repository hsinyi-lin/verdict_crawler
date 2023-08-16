from datetime import date
import openai, time, datetime
from opencc import OpenCC


with open('openai_key.txt', 'r') as file:
    api_key = file.read().strip()

openai.api_key = api_key


def to_traditional_text(text):
    cc = OpenCC('s2t')
    traditional_text = cc.convert(text)

    return traditional_text


def roc_to_ad(roc_date_str):
    roc_year, roc_month, roc_day = map(int, roc_date_str.split("."))
    ad_year = roc_year + 1911
    ad_date = date(ad_year, roc_month, roc_day)
    return ad_date


def current_roc_year():
    currentDateTime = datetime.datetime.now()
    date = currentDateTime.date()

    current_year = date.year - 1911

    return current_year



def call_openai_title(incident):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "你是一個專門把犯罪過程產生12字標題並轉成繁體中文的助理"},
                {"role": "user", "content": f'根據以下內容，幫我產生12字以內的標題：彭家榮於民國111年11月2日16時21分許，在家樂福仁愛分店（址設臺北市○○區○○路0段00○00號B1）內，趁店員疏未注意之際，竟意圖為自己不法之所有，基於竊盜之犯意，徒手接續竊取如附表所示之商品（共19件，總價值共計新臺幣【下同】1萬583元，下稱本案商品），並將本案商品藏放在外套口袋內而得手，得手後隨即逃逸。嗣經家樂福仁愛分店負責人林俊益發現本案商品遭竊，調閱監視器影像畫面並報警處理，始循線查悉上情。'},
                {"role": "assistant", "content": '家樂福店內商品遭竊取'},
                {"role": "user", "content": f'根據以下內容，幫我產生12字以內的標題：{incident}'},
        ]
    )

    response_message = completion['choices'][0]['message']['content'].strip()
    return to_traditional_text(response_message)


def call_openai_incident_lite(incident):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "你是一個專門把犯罪過程內容轉成口語化內容並繁體中文摘要的助理，只要回傳轉換後的內容結果就好，回傳的內容不能超過40字"},
                {"role": "user", "content": incident}
            ]
    )

    response_message = completion['choices'][0]['message']['content'].strip()
    return to_traditional_text(response_message)


def call_openai_find_features(incident, crime_id):
    if crime_id == 1:
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
    elif crime_id == 2:
        pass
    elif crime_id == 3:
        content = '簡伯宇意圖為自己不法之所有，基於攜帶兇器強盜之犯意，於民國111年8月26日凌晨5時30分許，持客觀上可供兇器使用之開山刀1支，進入苗栗縣○○鄉○○村○○00000號統一超商龍邦門市，以所持之開山刀指向該門市店員林建宏脖子、喝令林建宏開啟該門市內之收銀機抽屜，致使林建宏不能抗拒，依簡伯宇之要求開啟收銀機抽屜，簡伯宇隨即將收銀機內林建宏保管之新臺幣（下同）百元鈔及五百元鈔強行取走；繼之，再喝令林建宏開啟收銀台抽屜，再將該抽屜內林建宏保管之千元鈔及所有現金強行取走，得手後隨即駕車離去。嗣經林建宏會同該門市店長余朋綦清點核算結果，共損失4萬9,710元，員警據報持本院核發之搜索票前往臺中市○○區○○路00號13樓簡伯宇住處執行搜索，扣得簡伯宇行強盜時持用之開山刀1支及穿著之衣服、褲子、鞋子，始查悉上情。'
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個根據犯罪過程專門負責回答使用者一連串問題並且依序題目只會回答是或否的助理，並且每個問題都用頓號(、)來區隔的助理"},
                {"role": "user", "content": f'{content}，是否導致受害者受傷、是否兩人(含)以上犯案、是否使用刀械、是否擁有前科、有計畫犯罪、是否被害人人數超過兩人(含)、是否提及犯案人因生活困境而強盜、是否毀損物品或建築'},
                {"role": "assistant", "content": '是、否、是、否、是、否、否、否'},
                {"role": "user", "content": f'{incident}，是否導致受害者受傷、是否兩人(含)以上犯案、是否使用刀械、是否擁有前科、有計畫犯罪、是否被害人人數超過兩人(含)、是否提及犯案人因生活困境而強盜、是否毀損物品或建築'},
            ]
        )
    elif crime_id == 4:
        pass

    # 竊盜
    # is_money_related, is_abandoned, is_indoor, is_destructive,
    # is_group_crime, is_transportation_used, has_criminal_record, is_income_tool


    # 強盜
    # is_victim_injured, is_group_crime, is_weapon_used, has_prior_record, is_planned, 
    # is_multi_victims, is_due_to_hardship, is_property_damaged

    response_message = completion['choices'][0]['message']['content'].strip()
    clean_list = response_message.split('、')

    if len(clean_list) != 8:
        return False
    
    # 若特徵不等於8，需要加上判斷式
    clean = []
    for item in clean_list:
        if '否' in item or '不是' in item:
            clean.append(False)
        else:
            clean.append(True)

    # print(clean)

    return clean


def call_openai_prison_term(result, crime_id):
    if crime_id == 1:
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
    elif crime_id == 2:
        pass
    elif crime_id == 3:
        content = ['甲○○犯攜帶兇器強盜罪，累犯，處有期徒刑柒年貳月。扣案之開山刀壹把沒收。',  '陳富強犯結夥三人以上攜帶兇器強盜罪，累犯，處有期徒刑捌年。扣案如附表所示之物均沒收。蔡昀倫犯結夥三人以上攜帶兇器強盜罪，處有期徒刑柒年貳月。', '甲○○犯結夥三人以上攜帶兇器強盜罪，累犯，處有期徒刑肆年貳月。丁○○成年人與少年犯結夥三人以上攜帶兇器強盜罪，處有期徒刑參年捌月。']
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個根據判決結果回答出有期徒刑幾年幾個月，並且中間用頓號(、)隔開，並只用阿拉伯數字回答的助理"},
                {"role": "user", "content": f'{content[0]}，根據內容，有期徒刑幾年幾個月，如果超過一人被判有期徒刑就回傳判最久的那個人的'},
                {"role": "assistant", "content": '7、2'},
                {"role": "user", "content": f'{content[1]}，根據內容，有期徒刑幾年幾個月，如果超過一人被判有期徒刑就回傳判最久的那個人的'},
                {"role": "assistant", "content": '8、0'},
                {"role": "user", "content": f'{content[2]}，根據內容，有期徒刑幾年幾個月，如果超過一人被判有期徒刑就回傳判最久的那個人的'},
                {"role": "assistant", "content": '4、2'},
                {"role": "user", "content": f'{result}，根據內容，有期徒刑幾年幾個月，如果超過一人被判有期徒刑就回傳判最久的那個人的'},
            ]
        )
    elif crime_id == 4:
        pass

    response_message = completion['choices'][0]['message']['content'].strip()
    print(response_message)

    if crime_id == 1:
        try:
            month = int(response_message)
        except:
            return False
        return month
    elif crime_id == 2:
        pass
    elif crime_id == 3:
        # 拆解判刑年月
        prison_list = list(map(int, response_message.split('、')))
        if len(prison_list) > 2:
            return False
        
        # 回傳判刑年數月數、總月數(透過計算)
        return prison_list + [prison_list[0]*12 + prison_list[1]]
    elif crime_id == 4:
        pass
    