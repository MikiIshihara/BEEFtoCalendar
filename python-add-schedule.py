import datetime, re
import googleapiclient.discovery
import google.auth

# 編集スコープの設定(今回は読み書き両方OKの設定)
SCOPES = ['https://www.googleapis.com/auth/calendar']
# カレンダーIDの設定(基本的には自身のgmailのアドレス)
calendar_id = 'ここにメアドをいれる@gmail.com'

# 認証ファイルを使用して認証用オブジェクトを作成
gapi_creds = google.auth.load_credentials_from_file('credentials.json', SCOPES)[0]

# 認証用オブジェクトを使用してAPIを呼び出すためのオブジェクト作成
service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds)

# 追加するスケジュールの情報を設定
event= {
    # 予定のタイトル
    'summary': 'テスト！',
    # 予定の開始時刻(ISOフォーマットで指定)
    'start': {
        'dateTime': datetime.datetime(2021, 11, 30, 0, 00).isoformat(),
        'timeZone': 'Japan'
    },
    # 予定の終了時刻(ISOフォーマットで指定)
    'end': {
        'dateTime': datetime.datetime(2021, 12, 1, 17, 59).isoformat(),
        'timeZone': 'Japan'
    },
    #　予定の説明
    'description': 'テストテストテストテストです'
}

# 予定を追加する
event = service.events().insert(calendarId = calendar_id, body = event).execute()
