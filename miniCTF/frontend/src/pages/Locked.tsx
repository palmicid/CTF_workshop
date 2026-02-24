import { Link, useSearchParams } from "react-router-dom";

export default function Locked() {
    const [sp] = useSearchParams();
    const team = sp.get("team") || "";
    const unlocked = sp.get("unlocked") || "1";

    return (
        <div style={{ maxWidth: 720, margin: "40px auto", padding: 16 }}>
            <h2>Locked</h2>
            <p>You can’t jump ahead. Continue from your next unlocked level.</p>

            <p><b>Team:</b> {team}</p>

            <Link to={`/level/${unlocked}?team=${encodeURIComponent(team)}`}>
                <button>Go to Level {unlocked}</button>
            </Link>

            <div style={{ marginTop: 12 }}>
                <Link to="/">Back to Home</Link>
            </div>
        </div>
    );
}