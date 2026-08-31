#!/usr/bin/env python3
"""Download public uploads for the official YouTube channel into local JSON.

The key is read only from YOUTUBE_API_KEY. Never place it in this project.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "youtube-videos.json"
API_ROOT = "https://www.googleapis.com/youtube/v3"
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "UCGl-khGU26ic0cJMDIhmscg")

TERMS = {
    "Windows": ("windows", "win11", "win 11", "win10", "win 10", "powershell", "winget"),
    "Linux": ("linux", "ubuntu", "debian", "fedora", "arch", "hyprland", "gnome", "kde", "flatpak"),
    "Intelligenza artificiale": ("intelligenza artificiale", "chatgpt", "gemini", "claude", "copilot", "llm"),
}


def api_get(endpoint: str, params: dict[str, str], key: str) -> dict:
    query = dict(params)
    query["key"] = key
    try:
        with urlopen(f"{API_ROOT}/{endpoint}?{urlencode(query)}", timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"La richiesta YouTube non è riuscita (HTTP {error.code}).") from None
    except URLError:
        raise RuntimeError("Impossibile contattare YouTube Data API.") from None


def category_for(video: dict) -> str:
    title = video.get("title", "").lower()
    text = " ".join((video.get("title", ""), video.get("description", ""), " ".join(video.get("tags", [])))).lower()
    scores = {category: sum(text.count(term) for term in terms) for category, terms in TERMS.items()}
    best = max(scores, key=scores.get)
    if scores[best] == 0 or list(scores.values()).count(scores[best]) > 1:
        return "Altro"
    if scores[best] == 1 and not any(term in title for term in TERMS[best]):
        return "Altro"
    return best


def chunks(items: list[str], size: int = 50):
    for index in range(0, len(items), size):
        yield items[index:index + size]


def main() -> int:
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        print("Manca YOUTUBE_API_KEY nell'ambiente. Nessun dato è stato modificato.", file=sys.stderr)
        return 2

    channel = api_get("channels", {"part": "snippet,contentDetails", "id": CHANNEL_ID}, key)
    if not channel.get("items"):
        print("Canale ufficiale non trovato tramite YouTube Data API.", file=sys.stderr)
        return 3
    channel_item = channel["items"][0]
    uploads_id = channel_item["contentDetails"]["relatedPlaylists"]["uploads"]

    playlist_items, next_page = [], None
    while True:
        params = {"part": "snippet,contentDetails", "playlistId": uploads_id, "maxResults": "50"}
        if next_page:
            params["pageToken"] = next_page
        response = api_get("playlistItems", params, key)
        playlist_items.extend(response.get("items", []))
        next_page = response.get("nextPageToken")
        if not next_page:
            break

    video_ids = [item.get("contentDetails", {}).get("videoId") for item in playlist_items]
    video_ids = [video_id for video_id in video_ids if video_id]
    detailed, returned_ids = {}, set()
    for group in chunks(video_ids):
        response = api_get("videos", {"part": "snippet,contentDetails,statistics", "id": ",".join(group), "maxResults": "50"}, key)
        for item in response.get("items", []):
            detailed[item["id"]] = item
            returned_ids.add(item["id"])

    videos = []
    for item in playlist_items:
        video_id = item.get("contentDetails", {}).get("videoId")
        source = detailed.get(video_id)
        if not source:
            continue
        snippet = source.get("snippet", {})
        details = source.get("contentDetails", {})
        stats = source.get("statistics", {})
        video = {
            "videoId": video_id,
            "title": snippet.get("title", "Video senza titolo"),
            "description": snippet.get("description", ""),
            "publishedAt": snippet.get("publishedAt", item.get("snippet", {}).get("publishedAt", "")),
            "thumbnails": snippet.get("thumbnails", {}),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "viewCount": stats.get("viewCount"),
            "duration": details.get("duration"),
            "tags": snippet.get("tags", []),
            "categoryId": snippet.get("categoryId"),
        }
        video["category"] = category_for(video)
        videos.append(video)
    videos.sort(key=lambda video: video.get("publishedAt", ""), reverse=True)
    excluded = [{"videoId": video_id, "reason": "non pubblicamente recuperabile"} for video_id in video_ids if video_id not in returned_ids]
    payload = {
        "schemaVersion": 1,
        "status": "synced",
        "syncedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "channel": {"channelId": channel_item["id"], "title": channel_item.get("snippet", {}).get("title", ""), "uploadsPlaylistId": uploads_id},
        "videos": videos,
        "excluded": excluded,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Sincronizzati {len(videos)} video pubblici; esclusi {len(excluded)} elementi non recuperabili.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
