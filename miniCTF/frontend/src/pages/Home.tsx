import { Link } from "react-router-dom";

export default function Home() {
    return (
        <div style={{ maxWidth: 720, margin: "40px auto", padding: 16 }}>
            <h1>Cyber Escape</h1>
            <p>Choose an option:</p>

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <Link to="/new"><button>New Game</button></Link>
                <Link to="/continue"><button>Continue</button></Link>
                <Link to="/scoreboard"><button>Scoreboard</button></Link>
            </div>
        </div>
    );
}