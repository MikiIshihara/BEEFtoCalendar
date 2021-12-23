# 必要なモジュールをインポート
import pickle
import os.path
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']
CRED_FILE = 'credential_oauth.json'

# Google にcalendarへのアクセストークンを要求してcredsに格納します。
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

# カレンダーから予定を取得
events_result = service.events().list(calendarId="primary",
                                      # timeMin= now + str(datetime.timedelta(weeks=-8)),
                                      maxResults=30, singleEvents=True,
                                      orderBy='startTime').execute()
events = events_result.get('items', [])

# 予定がない場合には、Not found
if not events:
   print('No upcoming events found.')
# 予定があった場合には、出力
for event in events:
   start = event['start'].get('dateTime', event['start'].get('date'))
   if "課題" in event['summary']:
      print(start, event['summary'])
