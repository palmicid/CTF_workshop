const API_BASE = import.meta.env.VITE_API_BASE as string;

async function parseJson(res: Response) {
    const text = await res.text();
    try {
        return text ? JSON.parse(text) : {};
    } catch {
        return { ok: false, msg: "Invalid JSON from server" };
    }
}

export async function apiGet<T>(path: string): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, { method: "GET" });
    return (await parseJson(res)) as T;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    return (await parseJson(res)) as T;
}