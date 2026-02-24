import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiGet } from "../api/api";
import type { ScoreboardResp } from "../types";

export default function Scoreboard() {
    const [data, setData] = useState<ScoreboardResp | null>(null);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            const res = await apiGet<ScoreboardResp>("/scoreboard");
            if (!cancelled) setData(res);
        })();
        const t = setInterval(async () => {
            const res = await apiGet<ScoreboardResp>("/scoreboard");
            if (!cancelled) setData(res);
        }, 5000);
        return () => {
            cancelled = true;
            clearInterval(t);
        };
    }, []);

    return (
        <div style={{ maxWidth: 720, margin: "40px auto", padding: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
                <h2>Scoreboard</h2>
                <Link to="/">Home</Link>
            </div>

            {!data?.ok && <p>Loading…</p>}

            {data?.scores && (
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                        <tr>
                            <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>Team</th>
                            <th style={{ textAlign: "right", borderBottom: "1px solid #ddd", padding: 8 }}>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.scores.map((r) => (
                            <tr key={r.team}>
                                <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>{r.team}</td>
                                <td style={{ padding: 8, borderBottom: "1px solid #eee", textAlign: "right" }}>
                                    {r.score}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
            <p style={{ marginTop: 12, opacity: 0.8 }}>Auto-refresh every 5 seconds.</p>
        </div>
    );
}