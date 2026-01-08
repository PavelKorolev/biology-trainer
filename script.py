from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import date
from pathlib import Path
import json
import random
import os

# ================= APP =================

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "biology-secret")
)

templates = Jinja2Templates(directory="templates")

# ================= FILES =================

QUESTIONS_FILE = "questions_all.json"
PROGRESS_FILE = Path("progress.json")

# ================= LOAD QUESTIONS =================

with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    QUESTIONS_LIST = json.load(f)

QUESTIONS = {q["id"]: q for q in QUESTIONS_LIST}
ALL_IDS = sorted(QUESTIONS.keys())

# ================= PROGRESS =================

def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"days": {}, "questions": {}}

def save_progress(progress):
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

# ================= HARD QUESTIONS =================

def get_hard_questions(progress):
    hard = []
    qstats = progress.get("questions", {})

    for qid, stat in qstats.items():
        shown = stat.get("shown", 0)
        wrong = stat.get("wrong", 0)

        if shown >= 3 and (wrong >= 2 or wrong / shown >= 0.5):
            hard.append(int(qid))

    return sorted(hard)

# ================= HELPERS =================

def init_session(session, queue, mode):
    session.clear()
    session["queue"] = queue
    session["index"] = 0
    session["errors"] = []
    session["mode"] = mode
    session.pop("options_order", None)

# ================= ROUTES =================

@app.get("/start", response_class=HTMLResponse)
def start(request: Request):
    return templates.TemplateResponse("start.html", {"request": request})


@app.post("/start")
def start_post(
    request: Request,
    start: int = Form(1),
    end: int = Form(125),
    mode: str = Form("all")  # all | hard
):
    progress = load_progress()

    if mode == "hard":
        queue = get_hard_questions(progress)
        if not queue:
            # нет сложных — возвращаем на старт
            return RedirectResponse("/start", status_code=302)
    else:
        max_q = max(ALL_IDS)
        start = max(1, start)
        end = min(max_q, end)
        if start > end:
            start, end = end, start
        queue = [qid for qid in ALL_IDS if start <= qid <= end]

    init_session(request.session, queue, mode)
    return RedirectResponse("/", status_code=302)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    session = request.session

    if "queue" not in session or not session["queue"]:
        return RedirectResponse("/start", status_code=302)

    if session["index"] >= len(session["queue"]):
        if not session["errors"]:
            return RedirectResponse("/success", status_code=302)

        session["queue"] = session["errors"].copy()
        session["errors"] = []
        session["index"] = 0
        session["mode"] = "errors"
        session.pop("options_order", None)
        return RedirectResponse("/", status_code=302)

    qid = session["queue"][session["index"]]
    question = QUESTIONS[qid]

    # ---- фиксируем показ ----
    progress = load_progress()
    qstats = progress.setdefault("questions", {})
    stat = qstats.setdefault(str(qid), {"shown": 0, "wrong": 0})
    stat["shown"] += 1
    save_progress(progress)

    # ---- порядок вариантов ----
    if "options_order" not in session or session["options_order"]["qid"] != qid:
        items = list(question["options"].items())
        random.shuffle(items)
        session["options_order"] = {"qid": qid, "items": items}

    today = date.today().isoformat()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "question": question,
            "options_items": session["options_order"]["items"],
            "current": session["index"] + 1,
            "total": len(session["queue"]),
            "mode": session["mode"],
            "result": None,
            "selected": [],
            "progress": progress,
            "today": today
        }
    )


@app.post("/check", response_class=HTMLResponse)
def check(
    request: Request,
    id: int = Form(...),
    selected: list[str] = Form([])
):
    session = request.session
    question = QUESTIONS[id]

    correct = set(question["correct"])
    selected_set = set(selected)
    is_correct = selected_set == correct

    progress = load_progress()

    # ---- дневная статистика ----
    today = date.today().isoformat()
    days = progress.setdefault("days", {})
    day = days.get(today, {"answered": 0, "correct": 0})
    day["answered"] += 1
    if is_correct:
        day["correct"] += 1
    days[today] = day

    # ---- статистика вопроса ----
    if not is_correct:
        qstats = progress.setdefault("questions", {})
        stat = qstats.setdefault(str(id), {"shown": 0, "wrong": 0})
        stat["wrong"] += 1
        if id not in session["errors"]:
            session["errors"].append(id)

    save_progress(progress)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "question": question,
            "options_items": session["options_order"]["items"],
            "current": session["index"] + 1,
            "total": len(session["queue"]),
            "mode": session["mode"],
            "result": is_correct,
            "selected": selected,
            "progress": progress,
            "today": today
        }
    )


@app.post("/next")
def next_question(request: Request):
    request.session["index"] += 1
    request.session.pop("options_order", None)
    return RedirectResponse("/", status_code=302)


@app.get("/success", response_class=HTMLResponse)
def success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})


@app.get("/reset")
def reset(request: Request):
    request.session.clear()
    return RedirectResponse("/start", status_code=302)