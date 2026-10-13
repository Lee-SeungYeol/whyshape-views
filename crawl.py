# -*- coding: utf-8 -*-
"""유튜브와 틱톡의 공개 페이지에서 조회수를 읽어 data.json에 덧붙이고 index.html을 다시 만든다.
깃허브 액션이 30분마다 실행한다. 인스타그램은 로그인 없이는 읽히지 않아 지난 값을 그대로 둔다
(인스타그램 값은 PC의 Claude가 크롬으로 읽어 따로 넣는다). 읽지 못한 값도 지난 값을 유지한다."""
import datetime, json, os, re, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
CHANNEL = "UCNX_dFv0DFbsArdA1daP54w"
TIKTOK_USER = "why.this.shape"


def get(url, extra=None):
    h = dict(UA)
    h.update(extra or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def num(text):
    """'조회수 1.2천회', '460', '1.5만' 같은 표기를 정수로."""
    text = text.replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*(천|만|억|K|M)?", text)
    if not m:
        return None
    return int(float(m.group(1)) * {"천": 1e3, "만": 1e4, "억": 1e8, "K": 1e3, "M": 1e6, None: 1}[m.group(2)])


def youtube():
    """채널 Shorts 탭에서 영상별 조회수와 구독자 수를 읽는다."""
    out, subs = {}, None
    html = get(f"https://www.youtube.com/channel/{CHANNEL}/shorts", {"Cookie": "CONSENT=YES+1; SOCS=CAI"})
    # 페이지 안에서 '조회수 N회' 글자가 먼저 나오고 바로 뒤에 그 영상의 id가 나온다
    for label, vid in re.findall(r'"accessibilityText":"([^"]*?조회수[^"]*?)".{0,6000}?"videoId":"([\w-]{11})"', html, re.S):
        m = re.search(r"조회수\s*([\d.,]+\s*[천만억]?)\s*회", label)
        if m and vid not in out:
            out[vid] = num(m.group(1))
    m = re.search(r"구독자\s*([\d.,]+\s*[천만억]?)\s*명", html)
    if m:
        subs = num(m.group(1))
    return out, subs


def tiktok(video_id):
    html = get(f"https://www.tiktok.com/@{TIKTOK_USER}/video/{video_id}")
    m = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', html, re.S)
    s = m.group(1) if m else ""
    pick = lambda k: (lambda x: int(x.group(1)) if x else None)(re.search(r'"%s":\s*"?(\d+)' % k, s))
    return {"tiktok": pick("playCount"), "tt_likes": pick("diggCount"), "tt_comments": pick("commentCount")}


def tiktok_followers():
    html = get(f"https://www.tiktok.com/@{TIKTOK_USER}")
    m = re.search(r'"followerCount":\s*(\d+)', html)
    return int(m.group(1)) if m else None


CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
IG_PROFILE = os.path.join(os.path.expanduser("~"), "tools", "whyshape-chrome-profile")
IG_STAMP = os.path.join(os.path.expanduser("~"), "tools", "whyshape-insta-last.txt")
IG_EVERY = 15 * 60  # 인스타그램은 15분에 한 번만 연다(계정에 무리가 가지 않게)


def instagram():
    """PC에서만: 인스타그램에 로그인해 둔 크롤러 전용 크롬을 화면 없이 띄워 릴스 조회수를 읽는다.
    전용 크롬이 없거나, 창이 열려 있거나, 로그인이 풀렸으면 None을 돌려준다."""
    import time
    if not (os.path.isdir(IG_PROFILE) and os.path.isfile(CHROME)):
        return None
    try:
        if time.time() - float(open(IG_STAMP).read()) < IG_EVERY:
            return None
    except Exception:
        pass
    try:
        html = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--user-data-dir=" + IG_PROFILE, "--window-size=1200,2400",
                               "--virtual-time-budget=15000", "--dump-dom", "https://www.instagram.com/why_this_shape/reels/"],
                              capture_output=True, timeout=90).stdout.decode("utf-8", "replace")
    except Exception:
        return None
    open(IG_STAMP, "w").write(str(time.time()))
    out = {}
    for code, body in re.findall(r'href="/why_this_shape/reel/([\w-]+)/"(.{0,20000}?)</a>', html, re.S):
        nums = [num(x) for x in re.findall(r"<span[^>]*>\s*([\d.,]+\s*[천만억KM]?)\s*</span>", body)]
        if nums and code not in out:
            out[code] = nums[-1]
    m = re.search(r"팔로워\s*([\d.,]+[천만억]?)명[^\"]*?게시물\s*([\d.,]+)개", html)
    if m:
        out["__followers"], out["__posts"] = num(m.group(1)), num(m.group(2))
    return out if any(not k.startswith("__") for k in out) else None


def main():
    data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
    videos = json.load(open(os.path.join(HERE, "videos.json"), encoding="utf-8"))
    last = data["snapshots"][-1]
    prev = {v["id"]: v for v in last["videos"]}
    log = []
    try:
        yt, subs = youtube()
    except Exception as e:
        yt, subs = {}, None
        log.append(f"youtube 실패: {e}")
    ig = instagram()
    log.append("인스타 읽음" if ig else "인스타 건너뜀")
    snap_videos = []
    for cfg in videos:
        v = dict(prev.get(cfg["id"], {"tiktok": 0, "tt_likes": 0, "tt_comments": 0, "youtube": 0, "insta": 0}))
        v.update({"id": cfg["id"], "title": cfg["title"], "posted": cfg["posted"]})
        if yt.get(cfg.get("youtube")) is not None:
            v["youtube"] = yt[cfg["youtube"]]
        if cfg.get("tiktok"):
            try:
                for k, val in tiktok(cfg["tiktok"]).items():
                    if val is not None:
                        v[k] = val
            except Exception as e:
                log.append(f"tiktok {cfg['id']} 실패: {e}")
        if ig and ig.get(cfg.get("insta")) is not None:
            v["insta"] = ig[cfg["insta"]]
        snap_videos.append(v)
    followers = dict(last["followers"])
    if subs is not None:
        followers["youtube"] = subs
    try:
        f = tiktok_followers()
        if f is not None:
            followers["tiktok"] = f
    except Exception as e:
        log.append(f"tiktok 팔로워 실패: {e}")
    posts = last.get("insta_posts", 0)
    if ig:
        followers["instagram"] = ig.get("__followers", followers.get("instagram", 0))
        posts = ig.get("__posts", posts)
    kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    data["snapshots"].append({"at": kst.strftime("%Y-%m-%d %H:%M"), "followers": followers, "insta_posts": posts, "videos": snap_videos})
    json.dump(data, open(os.path.join(HERE, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, "build.py")], check=True)
    print("저장:", kst.strftime("%H:%M"), {v["id"]: (v["tiktok"], v["youtube"], v.get("insta")) for v in snap_videos}, "|", "; ".join(log) or "오류 없음")


if __name__ == "__main__":
    main()
