import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiPost } from "../api/api";
import type { ContinueResp } from "../types";

export default function Continue() {
    const [team, setTeam] = useState("");
    const [err, setErr] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const nav = useNavigate();

    async function submit() {
        setErr(null);
        const name = team.trim();
        if (!name) return setErr("Please enter your team name.");

        setLoading(true);
        try {
            const res = await apiPost<ContinueResp>("/continue", { team: name });
            if (!res.ok) {
                setErr(res.msg || "Team not found.");
                return;
            }
            const next = res.next_level ?? 1;
            nav(`/level/${next}?team=${encodeURIComponent(name)}`);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={{ maxWidth: 720, margin: "40px auto", padding: 16 }}>
            <h2>Continue</h2>
            <p>Enter the team name you used before.</p>

            <input
                value={team}
                onChange={(e) => setTeam(e.target.value)}
                placeholder="Team name"
                style={{ width: "100%", padding: 10, marginTop: 8 }}
            />

            <div style={{ marginTop: 12 }}>
                <button onClick={submit} disabled={loading}>
                    {loading ? "Loading..." : "Continue"}
                </button>
            </div>

            {err && <p style={{ color: "crimson", marginTop: 12 }}>{err}</p>}
        </div>
    );
}