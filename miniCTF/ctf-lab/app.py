from flask import Flask, request, jsonify, make_response, send_from_directory, abort
import base64
import os

app = Flask(__name__)

# These are "internal" values for the lab.
# They are NOT your main-platform answers; the player will extract these through actions.
# Your main platform should still validate Level 11-15 with your own FLAGS mapping.
LAB_FLAGS = {
    11: "crawler_found_this",
    12: "js_decoded",
    13: "cookie",
    14: "api_leak",
    15: "root_access_granted",  # boss level (harder)
}

# --- Helpers ---
def b64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")

# --- Home ---
@app.get("/")
def home():
    return """
    <h1>CTF Lab (Levels 11–15)</h1>
    <p>Open a level:</p>
    <ul>
      <li><a href="/level/11">Level 11</a></li>
      <li><a href="/level/12">Level 12</a></li>
      <li><a href="/level/13">Level 13</a></li>
      <li><a href="/level/14">Level 14</a></li>
      <li><a href="/level/15">Level 15</a></li>
    </ul>
    <p><b>Tip:</b> Use Developer Tools (Network / Application / Sources).</p>
    """


# ============================================================
# LEVEL 6 — Deploy web in hurry
# ============================================================

@app.get("/level/6")
def level6():
    return """
    <h1>Hello Welcome</h1>
    <p> where is the key? I don't konw I drop it here somewhere </p>
    <p> is this are dev environment or production? </p>
    <!-- TODO: remove before production
     access_key = network-->
    """

# ============================================================
# LEVEL 9 — When 1 step encode is not enough
# ============================================================

@app.get("/level/9")
def level9():
    return """
    <h1> Hints are here :) </h1>
    <p>"<strong>Step 1</strong>: Base64 decode the string.", <br>
    "<strong>Step 2</strong>: Reverse the decoded text.", <br>
    "<strong>Step 3</strong>: Caesar shift back by 1 (each letter -1)."
    </p>
    """

# ============================================================
# LEVEL 11 — robots.txt discovery (no flag in source)
# ============================================================

@app.get("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /hidden-panel\n"

@app.get("/level/11")
def level11():
    return """
    <h2>Level 11 — Hidden Directory</h2>
    <p>This server might have <b>robots.txt</b>.</p>
    <p>Find hidden paths and reach the correct place.</p>
    <p><i>Submit the value you discover to your main platform.</i></p>
    """

@app.get("/hidden-panel")
def hidden_panel():
    # No flag in HTML comments.
    # The user must click a button that calls an API endpoint.
    return """
    <h3>Hidden Panel</h3>
    <p>You're close. Prove you arrived here.</p>
    <button onclick="fetch('/api/level11/reveal', {method:'POST'}).then(r=>r.json()).then(d=>alert(d.flag))">
      Reveal
    </button>
    """

@app.post("/api/level11/reveal")
def level11_reveal():
    return jsonify({"ok": True, "flag": f"FLAG{{{LAB_FLAGS[11]}}}"})


# ============================================================
# LEVEL 12 — JavaScript base64 pieces (flag only via API)
# ============================================================

@app.get("/level/12")
def level12():
    return """
    <h2>Level 12 — JavaScript Inspection</h2>
    <p>The answer is not printed on the page.</p>
    <p>Inspect the JS file loaded by this page.</p>

    <script src="/static/level12.js"></script>
    <p>Open DevTools → Sources, read <code>level12.js</code>, and follow the hints.</p>
    """

@app.get("/static/level12.js")
def level12_js():
    # We do NOT include the final FLAG directly.
    # We include two base64 strings that become a key; then player calls /api/level12/unlock with that key.
    part1 = b64("unlock_")
    part2 = b64("level12")
    return (
        "/* Level 12 JS */\n"
        f"const p1 = '{part1}';\n"
        f"const p2 = '{part2}';\n"
        "console.log('Hint: base64 decode p1 and p2, join them.');\n"
        "console.log('Then POST JSON { key: <joined> } to /api/level12/unlock');\n"
    ), 200, {"Content-Type": "application/javascript"}

@app.post("/api/level12/unlock")
def level12_unlock():
    data = request.get_json(silent=True) or {}
    key = (data.get("key") or "").strip()
    if key != "unlock_level12":
        return jsonify({"ok": False, "msg": "wrong key"}), 403
    return jsonify({"ok": True, "flag": f"FLAG{{{LAB_FLAGS[12]}}}"})


# ============================================================
# LEVEL 13 — Cookie investigation (decode cookie then verify)
# ============================================================

@app.get("/level/13")
def level13():
    # set a cookie containing base64("flag=cookie")
    resp = make_response("""
    <h2>Level 13 — Cookie Clue</h2>
    <p>This page sets a cookie.</p>
    <p>DevTools → Application → Cookies</p>
    <p>Decode the cookie value.</p>
    <p>Then POST JSON { value: <decoded> } to <code>/api/level13/verify</code>.</p>
    """)
    resp.set_cookie("auth", b64("flag=cookie"), httponly=False)
    return resp

@app.post("/api/level13/verify")
def level13_verify():
    data = request.get_json(silent=True) or {}
    value = (data.get("value") or "").strip().lower()
    if value != "flag=cookie":
        return jsonify({"ok": False, "msg": "wrong decoded value"}), 403
    return jsonify({"ok": True, "flag": f"FLAG{{{LAB_FLAGS[13]}}}"})


# ============================================================
# LEVEL 14 — API discovery (network tab to find endpoint)
# ============================================================

@app.get("/level/14")
def level14():
    return """
    <h2>Level 14 — API Discovery</h2>
    <p>This page loads data from an internal API.</p>
    <p>Open DevTools → Network tab and refresh.</p>
    <div id="out"></div>

    <script>
      fetch('/api/v2/status')
        .then(r=>r.json())
        .then(d=>{
          document.getElementById('out').innerText = JSON.stringify(d, null, 2);
        });
    </script>
    """

@app.get("/api/v2/status")
def api_v2_status():
    # Include the flag in JSON (as per your earlier design), which is fine because it’s obtained by discovery.
    return jsonify({
        "status": "ok",
        "version": "v2",
        "note": "If you can see this, you found the internal endpoint.",
        "debug_flag": f"FLAG{{{LAB_FLAGS[14]}}}"
    })


# ============================================================
# LEVEL 15 — Boss level (privilege escalation via debug param)
# ============================================================

@app.get("/level/15")
def level15():
    # No flag in HTML. Player must craft request to /api/level15/login
    return """
    <h2>Level 15 — Privilege Escalation (Boss)</h2>
    <p>A login system is running in development mode.</p>
    <p>Your goal: obtain admin access and retrieve the admin flag.</p>

    <h3>Login</h3>
    <input id="u" placeholder="username" />
    <input id="p" placeholder="password" />
    <button onclick="login()">Login</button>

    <pre id="res"></pre>

    <script>
      async function login(){
        const r = await fetch('/api/level15/login', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({
            username: document.getElementById('u').value,
            password: document.getElementById('p').value
          })
        });
        const d = await r.json();
        document.getElementById('res').innerText = JSON.stringify(d, null, 2);
      }
    </script>

    <p><b>Hint:</b> DevTools → Network → inspect the request payload.</p>
    <p><b>Hint:</b> Development features sometimes accept extra parameters.</p>
    """

@app.post("/api/level15/login")
def level15_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    debug = data.get("debug", False)

    # baseline behavior
    if username == "guest" and password == "guest":
        return jsonify({"ok": True, "role": "guest", "msg": "limited access"})

    # "vulnerability": debug mode + username=admin grants admin
    # Player learns to modify request payload manually in DevTools.
    if username == "admin" and debug is True:
        return jsonify({"ok": True, "role": "admin", "flag": f"FLAG{{{LAB_FLAGS[15]}}}"})

    return jsonify({"ok": False, "msg": "invalid credentials"}), 403


if __name__ == "__main__":
    # bind to container interface
    app.run(host="0.0.0.0", port=9011, debug=False)