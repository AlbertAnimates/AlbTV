import re
import requests
from datetime import datetime

M3U = "russia.m3u","albanian.m3u"
TIMEOUT = 12          # seconds to wait per stream
HEADERS = {"User-Agent": "VLC/3.0.20"}   # some CDNs reject bare python requests

def check(url):
    """Return True if the stream responds with actual media bytes."""
    try:
        # stream=True + small chunk = we don't download the whole thing
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True, allow_redirects=True)
        if r.status_code != 200:
            return False
        ctype = r.headers.get("Content-Type", "").lower()
        # accept common streaming types; reject obvious HTML error pages
        ok_type = any(t in ctype for t in [
            "mpegurl", "mp2t", "video/", "audio/", "octet-stream", "application/"
        ])
        if "text/html" in ctype:
            return False
        # read a tiny bit to confirm it's not an empty response
        chunk = next(r.iter_content(chunk_size=2048), b"")
        return ok_type and len(chunk) > 0
    except Exception:
        return False

def main():
    with open(M3U, encoding="utf-8") as f:
        lines = f.read().splitlines()

    out = []
    alive = dead = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        # a channel header is followed by its URL on the next non-empty line
        if line.startswith("#EXTINF"):
            url_idx = i + 1
            while url_idx < len(lines) and lines[url_idx].strip() == "":
                url_idx += 1
            url = lines[url_idx].strip() if url_idx < len(lines) else ""

            already_dead = "[DEAD]" in line
            live = check(url) if url else False

            if live:
                alive += 1
                # revive a previously-dead channel that came back online
                out.append(line.replace(" [DEAD]", ""))
            else:
                dead += 1
                # tag it but KEEP it in the list (never silently delete)
                if already_dead:
                    out.append(line)
                else:
                    out.append(line.rstrip() + " [DEAD]")
            # copy the URL line(s) through unchanged
            for j in range(i + 1, url_idx + 1):
                out.append(lines[j])
            i = url_idx + 1
        else:
            out.append(line)
            i += 1

    with open(M3U, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    total = alive + dead
    stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    summary = f"# AlbTV validation {stamp} — {alive}/{total} alive, {dead} dead\n"
    # put the summary at the very top (after #EXTM3U / #PLAYLIST if present)
    if out and out[0].startswith("#EXTM3U"):
        out.insert(1, summary)
    else:
        out.insert(0, summary)
    with open(M3U, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    print(f"validated {total} channels: {alive} alive, {dead} dead")

if __name__ == "__main__":
    main()
