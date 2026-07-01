from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

# staticフォルダを使えるようにする
app.mount("/static", StaticFiles(directory="static"), name="static")

# templatesフォルダ設定
templates = Jinja2Templates(directory="templates")


# =========================
# Google Sheets 接続設定
# =========================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(creds)

# スプレッドシート名
sheet = client.open("学園祭管理").sheet1


# =========================
# トップページ
# =========================

@app.get("/")
def home(request: Request):

    # スプレッドシートのデータ取得
    rooms = sheet.get_all_records()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "rooms": rooms
        }
    )


# =========================
# 状態更新
# =========================

@app.post("/update_status")
def update_status(
    room_id: int = Form(...),
    status: str = Form(...)
):

    # 全データ取得
    records = sheet.get_all_records()

    # room_id に対応する行を探す
    for i, room in enumerate(records):

        if room["id"] == room_id:

            # スプレッドシートの行番号
            # +2 なのは:
            # 1行目 = ヘッダー
            # 0始まり補正
            row_number = i + 2

            # status列更新
            # C列なので3
            sheet.update_cell(row_number, 3, status)

            break

    return RedirectResponse(
        url="/",
        status_code=303
    )

@app.post("/add_room")
def add_room(
    name: str = Form(...),
    desks: int = Form(...),
    chairs: int = Form(...)
):

    # 現在データ取得
    records = sheet.get_all_records()

    # 新しいID
    new_id = len(records)

    # 新しい行追加
    sheet.append_row([
        new_id,
        name,
        "未確認",
        desks,
        chairs
    ])

    return RedirectResponse(
        url="/",
        status_code=303
    )
