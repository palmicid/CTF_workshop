import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams, Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { apiGet, apiPost } from "../api/api";
import type { LevelResp, SubmitResp } from "../types";
import rehypeRaw from "rehype-raw";

function useTeamFromQuery(): string {
    const [sp] = useSearchParams();
    return sp.get("team") || "";
}

export default function Level() {
    const { id } = useParams();
    const levelId = Number(id || "0");
    const team = useTeamFromQuery();
    const nav = useNavigate();

    const [data, setData] = useState<LevelResp | null>(null);
    const [answer, setAnswer] = useState("");
    const [msg, setMsg] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const backendBase = (import.meta.env.VITE_BACKEND_BASE as string) || "";

    const downloadHref = useMemo(() => {
        if (!data?.has_download || !data.download_url) return null;
        // download_url comes from backend like "/api/download/11"
        // Add team so backend can enforce locked levels
        return `${backendBase}${data.download_url}?team=${encodeURIComponent(team)}`;
    }, [data, team, backendBase]);

    useEffect(() => {
        if (!team) {
            nav("/continue");
            return;
        }
        let cancelled = false;

        (async () => {
            const res = await apiGet<LevelResp>(`/level/${levelId}?team=${encodeURIComponent(team)}`);
            if (cancelled) return;

            if (!res.ok && res.locked) {
                nav(`/locked?team=${encodeURIComponent(team)}&unlocked=${res.unlocked_level ?? 1}`);
                return;
            }
            if (!res.ok) {
                setMsg(res.msg || "Failed to load level.");
                setData(null);
                return;
            }
            setData(res);
            setMsg(null);
        })();

        return () => {
            cancelled = true;
        };
    }, [levelId, team, nav]);

    async function submitAnswer() {
        if (!team) return;
        setMsg(null);
        const a = answer.trim();
        if (!a) return setMsg("Please enter an answer.");

        setLoading(true);
        try {
            const res = await apiPost<SubmitResp>("/submit", {
                team,
                level: levelId,
                answer: a,
            });

            if (res.ok) {
                setMsg("✅ Correct!");
                setAnswer("");
                const next = res.next_level ?? levelId + 1;
                if (res.finished) {
                    nav(`/scoreboard`);
                } else {
                    // go to next level
                    nav(`/level/${next}?team=${encodeURIComponent(team)}`);
                }
            } else {
                setMsg(res.msg === "wrong" ? "❌ Wrong. Try again." : (res.msg || "❌ Failed."));
            }
        } finally {
            setLoading(false);
        }
    }

    if (!team) return null;

    return (
        <div style={{ maxWidth: 900, margin: "40px auto", padding: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                <h2>Level {levelId}{data?.title ? ` — ${data.title}` : ""}</h2>
                <div style={{ display: "flex", gap: 12 }}>
                    <Link to="/">Home</Link>
                    <Link to="/scoreboard">Scoreboard</Link>
                </div>
            </div>

            <p><b>Team:</b> {team}</p>

            <div style={{ padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
                {data?.instructions_md ? (
                    <ReactMarkdown rehypePlugins={[rehypeRaw]}>{data.instructions_md}</ReactMarkdown>
                ) : (
                    <p>Loading instructions…</p>
                )}
            </div>

            {downloadHref && (
                <div style={{ marginTop: 16 }}>
                    <a href={downloadHref}>
                        <button>Download CTF Lab (zip)</button>
                    </a>
                    <p style={{ marginTop: 8, opacity: 0.8 }}>
                        Extract the zip, then run <code>./run.sh</code>. Open the URL shown (usually{" "}
                        <code>http://localhost:9011</code>).
                    </p>
                </div>
            )}

            <div style={{ marginTop: 20 }}>
                <label>Answer</label>
                <input
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder="Type your answer"
                    style={{ width: "100%", padding: 10, marginTop: 8 }}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") submitAnswer();
                    }}
                />
                <button onClick={submitAnswer} disabled={loading} style={{ marginTop: 12 }}>
                    {loading ? "Checking..." : "Check Answer"}
                </button>
            </div>

            {msg && <p style={{ marginTop: 12 }}>{msg}</p>}
        </div>
    );
}