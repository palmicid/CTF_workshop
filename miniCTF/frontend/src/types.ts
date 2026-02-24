export type ApiOk<T> = T & { ok: boolean; msg?: string };

export interface NewGameResp {
    ok: boolean;
    team?: string;
    next_level?: number;
    msg?: string;
}

export interface ContinueResp {
    ok: boolean;
    team?: string;
    next_level?: number;
    msg?: string;
}

export interface LevelResp {
    ok: boolean;
    locked?: boolean;
    unlocked_level?: number;

    team?: string;
    level?: number;
    title?: string;
    instructions_md?: string;
    has_download?: boolean;
    download_url?: string; // starts with /api/...
    solved?: boolean;

    msg?: string;
}

export interface SubmitResp {
    ok: boolean;
    msg?: string;
    next_level?: number;
    finished?: boolean;
}

export interface ScoreboardResp {
    ok: boolean;
    scores?: { team: string; score: number }[];
}