import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import NewGame from "./pages/NewGame";
import Continue from "./pages/Continue";
import Level from "./pages/Level";
import Scoreboard from "./pages/Scoreboard";
import Locked from "./pages/Locked";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/new" element={<NewGame />} />
        <Route path="/continue" element={<Continue />} />
        <Route path="/level/:id" element={<Level />} />
        <Route path="/scoreboard" element={<Scoreboard />} />
        <Route path="/locked" element={<Locked />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}