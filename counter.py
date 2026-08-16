import re

PLAYLISTS = ["russia.m3u", "albania.m3u"]   # add more lists here later
README = "README.md"

def count_all():
    total = 0
    for m3u in PLAYLISTS:
        try:
            with open(m3u, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("#EXTINF"):
                        total += 1          # every channel, alive or [DEAD]
        except FileNotFoundError:
            print(f"!! {m3u} not found, skipping")
    return total

def update_badge(total):
    try:
        with open(README, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("README.md not found, skipping badge"); return

    new_content, n = re.subn(
        r"(<!--LIVE-->).*?(<!--/LIVE-->)",
        rf"\g<1>{total}\2",
        content, count=1,
    )
    if n == 0:
        print("!! no <!--LIVE--> marker in README — add it first"); return
    if new_content == content:
        print(f"badge unchanged at {total}"); return

    with open(README, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ badge → {total} total channels")

if __name__ == "__main__":
    total = count_all()
    print(f"counted {total} channels across {PLAYLISTS}")
    update_badge(total)
