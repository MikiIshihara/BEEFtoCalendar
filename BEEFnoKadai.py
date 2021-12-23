import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from bs4 import BeautifulSoup
import re
import datetime, re
import googleapiclient.discovery
import google.auth



# BEEFにログインする
driver = webdriver.Remote(
    command_executor="http://localhost:4444/wd/hub",
    desired_capabilities=DesiredCapabilities.CHROME)
print("remote")
# driver.get("https://idp.center.kobe-u.ac.jp/idp/profile/SAML2/Redirect/SSO?execution=e1s1")
login_url = 'https://beef.center.kobe-u.ac.jp/2021' #11/30変えた
driver.get(login_url)
time.sleep(3)

LoginID_box = driver.find_element_by_id("j_username")
LoginID_box.send_keys('ここに自分の学籍番号アルファベットまでを入力')
password_box = driver.find_element_by_name("j_password")
password_box.send_keys('パスワードを入力')
login_button = driver.find_element_by_name("_eventId_proceed")
login_button.click()
time.sleep(3)
driver.save_screenshot("beef_login_screenshot.png")
results = driver.find_elements_by_xpath("//div[@id='region-main-box']/*/*/div/div[@class='no-overflow']/p")
for element in results:
    print(element.text)


# ソースコードを取得
html = driver.page_source
# HTMLをパースする
soup = BeautifulSoup(html, 'lxml')
# CSSセレクタ
# selector = '{{ CSSセレクタ }}'

# ダッシュボード行く
ToDashboard = driver.find_element_by_css_selector("#label_2_2")
ToDashboard.click()
time.sleep(2)
results = driver.find_elements_by_xpath("//div[@id='page-wrapper']/nav/a/span")
for element in results:
    print(element.text)

# 直近のイベント　カレンダーへ移動をクリック
IdouCalendar = driver.find_element_by_css_selector("#inst78344 > div > div > div.footer > div > a")
print(IdouCalendar)
IdouCalendar.click()
time.sleep(2)

# maketransメソッドで変換テーブルを作成して、translateメソッドで置換
Henkan = { '年':',', '月':',', '日':'', ':':',', ' ':''}  # 年・月・日を「,」に、「:」を「, 」に、半角空白を削除
tbl = str.maketrans(Henkan) # 辞書dを基に変換テーブルを作成

# BeautifulSoupにページ情報をわたす
html = driver.page_source.encode('utf-8')
soup = BeautifulSoup(html, 'html.parser')

DaynEvent_tags = soup.find_all("td", class_="hasevent")


#　課題内容とってくる　
for tag in DaynEvent_tags:
    url = tag.find('a').get('href')
    driver.get(url)
    time.sleep(2)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    EventTitle = soup.find_all("h3", class_="name d-inline-block")
    print(EventTitle[0].text)

    EventDead_day = soup.find_all("h2", class_="current")
    EventDeadDayHenkan = re.sub("\(.+?\)", "",EventDead_day[0].text)
    EventDeadDayHenkan2 = EventDeadDayHenkan.translate(tbl).split(",")
    print(EventDeadDayHenkan2)

    EventDead_time = soup.find_all("div", class_="col-11")
    EventDeadTimeHenkan = EventDead_time[0].text.split(',')[1]
    # EventDeadTimeHenkan2 = EventDeadTimeHenkan.translate(tbl).split(",")
    # print(EventDeadTimeHenkan)
    print(EventDeadTimeHenkan)

    EventContent = soup.find_all("div", class_="description-content col-11")
    print(EventContent[0].text)

    EventSubject = soup.find_all(href=re.compile("course/view"))
    print(EventSubject[0].text)



# # 編集スコープの設定(今回は読み書き両方OKの設定)
#     SCOPES = ['https://www.googleapis.com/auth/calendar']
# # カレンダーIDの設定(基本的には自身のgmailのアドレス)
#     calendar_id = 'chiffon353@gmail.com'
#
#     # 認証ファイルを使用して認証用オブジェクトを作成
#     gapi_creds = google.auth.load_credentials_from_file('credentials.json', SCOPES)[0]
#
#     # 認証用オブジェクトを使用してAPIを呼び出すためのオブジェクト作成
#     service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds)
#
#     # 追加するスケジュールの情報を設定
#     event= {
#         # 予定のタイトル
#         'summary': EventDeadTimeHenkan + EventTitle[0].text ,
#         # 予定の開始時刻(ISOフォーマットで指定)
#         'start': {
#             'dateTime': datetime.datetime(int(EventDeadDayHenkan2[0]),int(EventDeadDayHenkan2[1]),int(EventDeadDayHenkan2[2]),0,0).isoformat(),
#             'timeZone': 'Japan'
#         },
#
#         # 予定の終了時刻(ISOフォーマットで指定)
#         'end': {
#             'dateTime': datetime.datetime(int(EventDeadDayHenkan2[0]),int(EventDeadDayHenkan2[1]),int(EventDeadDayHenkan2[2]),23,59).isoformat(),
#             'timeZone': 'Japan'
#         },
#         #　予定の説明
#         'description': EventContent[0].text + EventSubject[0].text
#     }
#
#
#
#
#
#     # 予定を追加する
#     event = service.events().insert(calendarId = calendar_id, body = event).execute()




driver.quit()
