# app.py
import os
import re
import time
from flask import Flask, request, jsonify, send_file, abort, send_from_directory
from flask_cors import CORS

import db
from config import HOST, PORT, DEBUG, TOTAL_LEVELS, BASE_DIR
from flags import FLAGS
from levels.level_data import LEVELS

app = Flask(__name__)
CORS(app)

db.init_db()

TEAM_RE = re.compile(r"^[A-Za-z0-9 _-]{1,30}$")

def clean_team(name: str) -> str:
    return (name or "").strip()

def valid_team(name: str) -> bool:
    return bool(TEAM_RE.match(name))

def read_md(path: str) -> str:
    abs_path = os.path.join(BASE_DIR, path)
    if not os.path.exists(abs_path):
        return "(No description file found yet.)"
    with open(abs_path, "r", encoding="utf-8") as f:
        return f.read()

def normalize_answer(s: str) -> str:
    # tolerant: ignore extra spaces + case
    return re.sub(r"\s+", "", (s or "").strip().lower())

@app.get("/api/health")
def health():
    return jsonify({"ok": True})

# Main page -> New Game
@app.post("/api/new-game")
def api_new_game():
    data = request.get_json(force=True)
    team = clean_team(data.get("team"))

    if not team:
        return jsonify({"ok": False, "msg": "team name required"}), 400
    if not valid_team(team):
        return jsonify({"ok": False, "msg": "team name must be 1-30 chars (letters/numbers/space/_- only)"}), 400

    created = db.create_team(team)
    if not created:
        return jsonify({"ok": False, "msg": "duplicate team name"}), 409

    return jsonify({"ok": True, "team": team, "next_level": 1})

# Main page -> Continue
@app.post("/api/continue")
def api_continue():
    data = request.get_json(force=True)
    team = clean_team(data.get("team"))

    if not team:
        return jsonify({"ok": False, "msg": "team name required"}), 400

    team_id = db.get_team_id(team)
    if not team_id:
        return jsonify({"ok": False, "msg": "team not found"}), 404

    nl = db.get_next_unlocked_level(team_id, TOTAL_LEVELS)
    return jsonify({"ok": True, "team": team, "next_level": nl})

# Level page data (React calls this)
@app.get("/api/level/<int:level_id>")
def api_level(level_id: int):
    team = clean_team(request.args.get("team"))
    if not team:
        return jsonify({"ok": False, "msg": "team is required"}), 400

    team_id = db.get_team_id(team)
    if not team_id:
        return jsonify({"ok": False, "msg": "team not found"}), 404

    if level_id < 1 or level_id > TOTAL_LEVELS:
        return jsonify({"ok": False, "msg": "invalid level"}), 404

    solved = db.get_solved_levels(team_id)
    unlocked = (max(solved) + 1) if solved else 1

    # allow viewing solved levels too, but do not allow future levels
    if level_id > unlocked and level_id not in solved:
        return jsonify({"ok": False, "locked": True, "unlocked_level": unlocked}), 403

    meta = LEVELS.get(level_id, {"title": f"Level {level_id}", "md": None, "download": None})
    instructions = read_md(meta["md"]) if meta.get("md") else "(No instructions yet.)"

    has_download = bool(meta.get("download"))
    download_url = f"/api/download/{level_id}" if has_download else None

    return jsonify({
        "ok": True,
        "team": team,
        "level": level_id,
        "title": meta.get("title", f"Level {level_id}"),
        "instructions_md": instructions,
        "has_download": has_download,
        "download_url": download_url,
        "unlocked_level": unlocked,
        "solved": (level_id in solved),
    })

# Answer checking
@app.post("/api/submit")
def api_submit():
    data = request.get_json(force=True)
    team = clean_team(data.get("team"))
    level_id = int(data.get("level") or 0)
    answer = (data.get("answer") or "").strip()

    if not team or not answer:
        return jsonify({"ok": False, "msg": "team and answer required"}), 400
    if level_id < 1 or level_id > TOTAL_LEVELS:
        return jsonify({"ok": False, "msg": "invalid level"}), 400

    team_id = db.get_team_id(team)
    if not team_id:
        return jsonify({"ok": False, "msg": "team not found"}), 404

    solved = db.get_solved_levels(team_id)
    unlocked = (max(solved) + 1) if solved else 1

    # prevent skipping: only submit the next unsolved level
    if level_id != unlocked:
        return jsonify({"ok": False, "msg": "level locked", "next_level": unlocked}), 403

    correct = FLAGS.get(level_id)
    if not correct:
        return jsonify({"ok": False, "msg": "flag not configured"}), 500

    # small anti-spam delay
    time.sleep(0.25)

    if normalize_answer(answer) == normalize_answer(correct):
        db.record_solve(team_id, level_id)
        next_level = db.get_next_unlocked_level(team_id, TOTAL_LEVELS)
        finished = (level_id == TOTAL_LEVELS)
        return jsonify({"ok": True, "msg": "correct", "next_level": next_level, "finished": finished})
    else:
        return jsonify({"ok": False, "msg": "wrong"}), 200

@app.get("/api/scoreboard")
def api_scoreboard():
    return jsonify({"ok": True, "scores": db.scoreboard()})

@app.get("/api/download/<int:level_id>")
def api_download(level_id: int):
    meta = LEVELS.get(level_id)
    if not meta or not meta.get("download"):
        return jsonify({"ok": False, "msg": "no download for this level"}), 404

    # Optional lock check (recommended)
    team = request.args.get("team", "").strip()
    team_id = db.get_team_id(team)
    if not team_id:
        return jsonify({"ok": False, "msg": "team not found"}), 404
    solved = db.get_solved_levels(team_id)
    unlocked = (max(solved) + 1) if solved else 1
    if level_id > unlocked:
        return jsonify({"ok": False, "msg": "level locked"}), 403

    if meta["download"] == "LAB_ZIP":
        zip_path = os.path.join(BASE_DIR, "levels", "lab", "ctf-lab.zip")
        if not os.path.exists(zip_path):
            return jsonify({"ok": False, "msg": "lab zip missing"}), 404
        return send_file(zip_path, as_attachment=True, download_name="ctf-lab.zip")

    file_path = os.path.join(BASE_DIR, meta["download"])
    if not os.path.exists(file_path):
        return jsonify({"ok": False, "msg": "file not found"}), 404

    return send_file(file_path, as_attachment=True, download_name=f"level{level_id:02d}_run.sh")

@app.get("/api/download/lab")
def api_download_lab():
    zip_path = os.path.join(BASE_DIR, "levels", "lab", "ctf-lab.zip")
    if not os.path.exists(zip_path):
        return jsonify({"ok": False, "msg": "lab zip missing"}), 404

    return send_file(
        zip_path,
        as_attachment=True,
        download_name="ctf-lab.zip"
    )

# Optional: reset (add a header token later)
@app.post("/api/admin/reset")
def api_admin_reset():
    db.reset_all()
    return jsonify({"ok": True})

# ===== Serve React Production Build =====

FRONTEND_DIST = os.path.join(BASE_DIR, "../frontend/dist")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    # If request is for API, let API routes handle it
    if path.startswith("api"):
        abort(404)

    # Serve static file if exists
    full_path = os.path.join(FRONTEND_DIST, path)
    if path != "" and os.path.exists(full_path):
        return send_from_directory(FRONTEND_DIST, path)

    # Otherwise serve index.html (SPA fallback)
    return send_from_directory(FRONTEND_DIST, "index.html")

@app.get("/api/hint/<int:level_id>/<int:hint_no>")
def api_hint(level_id: int, hint_no: int):
    team = clean_team(request.args.get("team"))
    if not team:
        return jsonify({"ok": False, "msg": "team is required"}), 400

    team_id = db.get_team_id(team)
    if not team_id:
        return jsonify({"ok": False, "msg": "team not found"}), 404

    if level_id < 1 or level_id > TOTAL_LEVELS:
        return jsonify({"ok": False, "msg": "invalid level"}), 404

    # enforce level access (no skipping)
    solved = db.get_solved_levels(team_id)
    unlocked = (max(solved) + 1) if solved else 1
    if level_id > unlocked and level_id not in solved:
        return jsonify({"ok": False, "msg": "level locked"}), 403

    meta = LEVELS.get(level_id, {})
    hints = meta.get("hints", [])
    if hint_no < 1 or hint_no > len(hints):
        return jsonify({"ok": False, "msg": "hint not found"}), 404

    return jsonify({"ok": True, "hint": hints[hint_no - 1], "hint_no": hint_no, "total": len(hints)})

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)