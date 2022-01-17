import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from bs4 import BeautifulSoup
import re
import datetime, re
import googleapiclient.discovery
import google.auth

# 必要なモジュールをインポート
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# BEEFにログインする
driver = webdriver.Remote(
    command_executor="http://localhost:4444/wd/hub",
    desired_capabilities=DesiredCapabilities.CHROME)
print("remote")
login_url = 'https://beef.center.kobe-u.ac.jp/2021' #11/30変えた
driver.get(login_url)
time.sleep(3)

LoginID_box = driver.find_element_by_id("j_username")
LoginID_box.send_keys('学番')
password_box = driver.find_element_by_name("j_password")
password_box.send_keys('パス')
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


# ダッシュボード行く
ToDashboard = driver.find_element_by_css_selector("#label_2_2")
ToDashboard.click()
time.sleep(2)
results = driver.find_elements_by_xpath("//div[@id='page-wrapper']/nav/a/span")
for element in results:
    print(element.text)

# 直近のイベント　カレンダーへ移動をクリック
# IdouCalendar = driver.find_element_by_css_selector("#inst78344 > div > div > div.footer > div > a")
IdouCalendar = driver.find_element_by_class_name("gotocal")
print(IdouCalendar)
IdouCalendar.click()
time.sleep(2)

# maketransメソッドで変換テーブルを作成して、translateメソッドで置換
Henkan = { '年':',', '月':',', '日':'', ':':',', ' ':''}  # 年・月・日を「,」に、「:」を「, 」に、半角空白を削除
tbl = str.maketrans(Henkan)

# BeautifulSoupにページ情報をわたす
html = driver.page_source.encode('utf-8')
soup = BeautifulSoup(html, 'html.parser')

DaynEvent_tags = soup.find_all("td", class_="hasevent")

# 編集スコープの設定(読み書き両方OKの設定)
SCOPES = ['https://www.googleapis.com/auth/calendar']

# カレンダーIDの設定(gmailのアドレス)
calendar_id = 'メアド@gmail.com'

CRED_FILE = 'credential_oauth.json'

# Googleにcalendarへのアクセストークンを要求してcredsに格納
creds = None

# 有効なトークンをすでに持っているかチェック（２回目以降の実行時に認証を省略するため）
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# 期限切れのトークンを持っているかチェック（認証を省略するため）
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    # アクセストークンを要求
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    # アクセストークン保存（２回目以降の実行時に認証を省略するため）
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

# 現在時刻を取得
now = datetime.datetime.utcnow().isoformat() + 'Z'

# Googleカレンダーから予定を取得
GoogleEvents_result = service.events().list(calendarId="primary",
                                      # timeMin= now + str(datetime.timedelta(weeks=-8)),
                                      maxResults=500,singleEvents=True,
                                      orderBy='startTime').execute()
events = GoogleEvents_result.get('items', [])

# Googleカレンダーに予定があった場合には、出力
for event in events:
   start = event['start'].get('dateTime', event['start'].get('date'))
   if "課題" in event['summary']:
      print(start, event['summary'])

#　BEEFから課題内容とってくる　
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
    print(EventDeadTimeHenkan)

    EventContent = soup.find_all("div", class_="description-content col-11")
    print(EventContent[0].text)

    EventSubject = soup.find_all(href=re.compile("course/view"))
    print(EventSubject[0].text)

    chouhuku = False
    if events:
        for event in events:
           if EventTitle[0].text in event['summary']:
              print("同じのあったで！")
              chouhuku = True
    else:
        # 予定がない場合には、Not found
        print('No upcoming events found.')

    if chouhuku:
        continue

    # Googleカレンダーに追加するスケジュールの情報を設定
    event= {
        # 予定のタイトル
        'summary': EventDeadTimeHenkan + EventTitle[0].text ,
        # 予定の開始時刻(ISOフォーマットで指定)
        'start': {
            'dateTime': datetime.datetime(int(EventDeadDayHenkan2[0]),int(EventDeadDayHenkan2[1]),int(EventDeadDayHenkan2[2]),0,0).isoformat(),
            'timeZone': 'Japan'
        },

        # 予定の終了時刻(ISOフォーマットで指定)
        'end': {
            'dateTime': datetime.datetime(int(EventDeadDayHenkan2[0]),int(EventDeadDayHenkan2[1]),int(EventDeadDayHenkan2[2]),23,59).isoformat(),
            'timeZone': 'Japan'
        },
        #　予定の説明
        'description': EventContent[0].text + EventSubject[0].text
    }

    # Googleカレンダーに予定を追加する
    event = service.events().insert(calendarId = calendar_id, body = event).execute()

    # LINEで通知を送信
    url = "https://notify-api.line.me/api/notify"
    access_token = 'ここに入れる'
    headers = {'Authorization': 'Bearer ' + access_token}

    message = [ "new!" + str(EventTitle[0].text) + " を追加しました" ]
    payload = {'message': message}
    r = requests.post(url, headers=headers, params=payload,)


driver.quit()
