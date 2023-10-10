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


def handling_newline(incident, result):
    # 處理換行問題(犯罪過程)
    tmp_incident = ''.join(incident.split())
    incident_list = tmp_incident.split('。')
    res = '。\n'.join(incident_list).strip()

    tmp_incident_list = res.split('：(')
    clean_incident = '：\n('.join(tmp_incident_list).strip()

    tmp_incident_list = clean_incident.split('：（')
    clean_incident = '：\n（'.join(tmp_incident_list).strip()

    # 處理換行問題(判決結果)
    tmp_result = ''.join(result.split())
    result_list = tmp_result.split('。')
    res = '。\n'.join(result_list).strip()

    tmp_result_list = res.split('：(')
    clean_result = '：\n('.join(tmp_result_list).strip()

    tmp_result_list = clean_result.split('：（')
    clean_result = '：\n（'.join(tmp_result_list).strip()

    return clean_incident, clean_result




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
        content = '丙○○與丁○○同住於雲林縣○○鄉○○村○○○0號之住處，2人間具有家庭暴力防治法第3條第2款所定之家庭成員關係。丙○○前因對丁○○實施家庭暴力行為，經本院於民國110年2月1日核發109年度家護字第735號民事通常保護令，裁定命丙○○不得對丁○○實施家庭暴力之行為，保護令有效期間自核發時起生效，有效期間為1年，丙○○並於110年2月7日中午12時45分，經雲林縣警察局臺西分局員警告知而知悉上開保護令內容。嗣丙○○於同年6月24日中午1時30分，在上址住處，因與丁○○有金錢爭執，明知人之頭部若遭壓制於水中，有導致窒息死亡之可能，仍基於殺人犯意及違反保護令之犯意，先徒手將丁○○之頭部按壓至裝有水之水桶內，經丁○○奮力抬起頭後，復接續將丁○○之頭部按壓入水桶內，並同時對其表示：「乎你死（臺語）」等語，再徒手毆打丁○○之頭部並以腳踹丁○○之身體、徒手拉扯丁○○之頭髮，經丙○○之母親乙○○發覺勸阻，然丙○○卻接續持菜刀砍傷丁○○之左腳，致丁○○受有右頸部疼痛及左小腿多處割傷等傷害，丙○○即以上開方式對丁○○實施家庭暴力行為，而違反上開保護令。幸經乙○○及時制止未造成丁○○之性命安危，丁○○始倖免於難而未遂。嗣乙○○報警，經警方到場處理，並當場逮捕丙○○，且扣得菜刀1把。'
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個根據犯罪過程專門負責回答使用者一連串問題並且依序題目只會回答是或否的助理，並且每個問題都用頓號(、)來區隔的助理"},
                {"role": "user", "content": f'{content}，是否有殺人未遂、是否被害者為兒童、是否有親屬關係、加害者是否有精神疾病、是否為金錢糾紛、在過去是否有犯過罪、是否為感情糾紛、是否在過去有仇恨'},
                {"role": "assistant", "content": '是、否、是、否、是、否、否、否、是'},
                {"role": "user", "content": f'{incident}，是否有殺人未遂、是否被害者為兒童、是否有親屬關係、加害者是否有精神疾病、是否為金錢糾紛、在過去是否有犯過罪、是否為感情糾紛、是否在過去有仇恨'},
            ]
        )
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
        content = '劉龍賢於民國105年4月16日4時許，在高雄市○○區○○路某處食用含酒精之食品及飲用啤酒後，而致其呼氣所含酒精濃度已逾每公升0.25毫克之法定標準，且其既可知悉上情，主觀上雖無致人於死之故意，然客觀上應能預見酒後逕行駕駛動力交通工具，倘發生車禍事故，可能引致他人死亡之結果，仍於同日8時40分許，駕駛車牌號碼000-000號普通重型機車欲返回住處。嗣於同日9時許，行經高雄市○○區○○街○巷○號而欲進入該址地下停車場入口時，本應注意車前狀況，並隨時採取必要之安全措施，而依當時天氣晴、日間自然光線、柏油路面狀態乾燥、無缺陷、無障礙物，視距良好，依其智識、能力並無不能注意之情事，竟因酒後注意力及控制力減弱，疏未注意車前狀況，見林龍生步行欲穿越該地下停車場入口，遂緊急煞車後人車倒地，其機車倒地滑行後擦撞林龍生，林龍生亦因此倒地，因而受有頭部外傷併顱內出血、顱骨骨折、嚴重腦水腫等傷害。林龍生經緊急送往高雄醫學大學附設中和紀念醫院（下稱高醫）急救後，仍於同月20日15時26分許，因中樞神經衰竭而不治死亡。而劉龍賢則於車禍發生後，犯罪未被發覺前，在現場等候並於警方到場時，自首而受裁判，並於同月16日9時13分許，經警方對其施以酒精濃度測試，測得其吐氣之酒精濃度達每公升0.59毫克，始知上情。'
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個根據犯罪過程專門負責回答使用者一連串問題並且依序題目只會回答是或否的助理，並且每個問題都用頓號(、)來區隔的助理"},
                {"role": "user", "content": f'{content}，是否有駕駛執照、是否搭載其他乘客、是否影響交通安全、是否造成他人財產損害、是否以駕駛車輛為職業、是否肇事逃逸、被撞者是否受有重傷、當天天氣是否晴朗'},
                {"role": "assistant", "content": '否、否、是、否、否、否、是、是'},
                {"role": "user", "content": f'{incident}，是否有駕駛執照、是否搭載其他乘客、是否影響交通安全、是否造成他人財產損害、是否以駕駛車輛為職業、是否肇事逃逸、被撞者是否受有重傷、當天天氣是否晴朗'},
            ]
        )

    # 竊盜
    # is_money_related, is_abandoned, is_indoor, is_destructive,
    # is_group_crime, is_transportation_used, has_criminal_record, is_income_tool

    # 殺人罪
    # is_attempted, is_child_victim, is_family_relation, is_mentally_ill
    # is_money_dispute, is_prior_record, is_emotional_dispute, is_intentional

    # 強盜
    # is_victim_injured, is_group_crime, is_weapon_used, has_prior_record, is_planned, 
    # is_multi_victims, is_due_to_hardship, is_property_damaged

    # 酒駕
    # has_driving_license, has_passengers, affected_traffic_safety, caused_property_damage
    # is_professional_driver, hit_and_run, victim_has_severe_injury, weather_was_clear


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
        content = ['趙志仁犯殺人罪，處有期徒刑拾貳年，褫奪公權陸年。又犯傷害罪，處有期徒刑肆月，如易科罰金，以新臺幣壹仟元折算壹日。扣案之剪刀貳把，均沒收之。']
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個根據判決結果回答出有期徒刑幾年幾個月，並且中間用頓號(、)隔開，並只用阿拉伯數字回答的助理"},
                {"role": "user", "content": f'{content[0]}，根據內容，有期徒刑幾年幾個月，如果超過一人被判有期徒刑就回傳判最久的那個人的'},
                {"role": "assistant", "content": '12、0'},
                {"role": "user", "content": f'{result}，根據內容，有期徒刑幾年幾個月，如果超過一人被判有期徒刑就回傳判最久的那個人的'},
            ]
        )
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
        content = ['杜宥賢犯不能安全駕駛動力交通工具因而致人於死罪，處有期徒刑肆年陸月。']
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個根據判決結果回答出有期徒刑幾年幾個月，並且中間用頓號(、)隔開，並只用阿拉伯數字回答的助理"},
                {"role": "user", "content": f'{content[0]}，根據內容，有期徒刑幾年幾個月，如果超過一人被判有期徒刑就回傳判最久的那個人的'},
                {"role": "assistant", "content": '4、6'},
                {"role": "user", "content": f'{result}，根據內容，有期徒刑幾年幾個月，如果超過一人被判有期徒刑就回傳判最久的那個人的'},
            ]
        )

    response_message = completion['choices'][0]['message']['content'].strip()
    print(response_message)

    if crime_id == 1:
        try:
            month = int(response_message)
        except:
            return False
        return month
    elif crime_id == 2:
        prison_list = list(map(int, response_message.split('、')))
        if len(prison_list) > 2:
            return False
        
        return prison_list + [prison_list[0]*12 + prison_list[1]]
    elif crime_id == 3:
        # 拆解判刑年月
        prison_list = list(map(int, response_message.split('、')))
        if len(prison_list) > 2:
            return False
        
        # 回傳判刑年數月數、總月數(透過計算)
        return prison_list + [prison_list[0]*12 + prison_list[1]]
    elif crime_id == 4:
        prison_list = list(map(int, response_message.split('、')))
        if len(prison_list) > 2:
            return False
        
        return prison_list + [prison_list[0]*12 + prison_list[1]]
    