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


def youtube_video(video_id):
    """영상 한 편의 페이지에서 정확한 조회수와 좋아요 수를 읽는다."""
    html = get(f"https://www.youtube.com/shorts/{video_id}", {"Cookie": "CONSENT=YES+1; SOCS=CAI"})
    pick = lambda k: (lambda x: int(x.group(1)) if x else None)(re.search(r'"%s":"?(\d+)' % k, html))
    return {"youtube": pick("viewCount"), "yt_likes": pick("likeCount")}


def tiktok(video_id):
    html = get(f"https://www.tiktok.com/@{TIKTOK_USER}/video/{video_id}")
    m = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', html, re.S)
    s = m.group(1) if m else ""
    pick = lambda k: (lambda x: int(x.group(1)) if x else None)(re.search(r'"%s":\s*"?(\d+)' % k, s))
    return {"tiktok": pick("playCount"), "tt_likes": pick("diggCount"), "tt_comments": pick("commentCount")}


def tiktok_desc(video_id):
    """틱톡 영상의 설명 글(올릴 때 적은 문구)."""
    html = get(f"https://www.tiktok.com/@{TIKTOK_USER}/video/{video_id}")
    m = re.search(r'"desc":"((?:[^"\\]|\\.)*)"', html)
    return json.loads('"' + m.group(1) + '"') if m else ""


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
            # 칸에 숫자가 3개면 좋아요·댓글·조회수. 좋아요가 0이면 인스타그램이 그 숫자를 아예 안 보여 줘서 개수가 줄어든다
            # (숫자 1개 = 조회수만 → 좋아요 0·댓글 0, 2개 = 좋아요·조회수 → 댓글 0 으로 본다)
            out[code] = {"insta": nums[-1], "ig_likes": nums[0] if len(nums) >= 2 else 0, "ig_comments": nums[1] if len(nums) >= 3 else 0}
    m = re.search(r"팔로워\s*([\d.,]+[천만억]?)명[^\"]*?게시물\s*([\d.,]+)개", html)
    if m:
        out["__followers"], out["__posts"] = num(m.group(1)), num(m.group(2))
    # 화면 머리말의 실제 숫자가 더 정확하다. 위의 og:description 값은 인스타그램이 늦게 고쳐서 팔로워가 생겨도 한동안 0명으로 남는다
    for word, key in (("팔로워", "__followers"), ("게시물", "__posts")):
        m = re.search(word + r"\s*<span[^>]*>(?:\s*<[^>]+>)*\s*([\d.,]+\s*[천만억]?)", html)
        if m and num(m.group(1)) is not None:
            out[key] = num(m.group(1))
    return out if any(not k.startswith("__") for k in out) else None

def tiktok_list(known):
    """틱톡의 공개 임베드 페이지에서 올라온 영상 번호를 읽는다(로그인·크롬 불필요, 깃허브에서도 된다).
    이미 아는 번호는 그대로 두고, 처음 보는 번호는 그 영상 페이지에서 조회수가 읽힐 때만 영상으로 인정한다."""
    import time
    stamp = os.path.join(HERE, ".tiktok-list-last")
    try:
        if time.time() - float(open(stamp).read()) < 15 * 60:  # 자주 열면 429로 막힌다. 15분에 한 번만.
            return None
    except Exception:
        pass
    html = get(f"https://www.tiktok.com/embed/@{TIKTOK_USER}")  # 503·429가 잦다. 실패하면 다음 회차(3분 뒤)에 다시 한다
    open(stamp, "w").write(str(time.time()))                     # 성공했을 때만 15분을 쉰다
    out = []
    for tid in sorted(set(re.findall(r"(?<!\d)(\d{19})(?!\d)", html))):  # 번호가 클수록 나중에 올린 것
        if tid in known:
            continue
        try:
            if tiktok(tid).get("tiktok") is not None:
                out.append(tid)
        except Exception:
            pass
    return out


def discover(videos, yt_ids, tt_ids, ig_codes, log):
    """videos.json에 없는 영상을 찾아 스스로 등록한다.
    유튜브에서 새 영상을 찾으면 제목과 올린 때를 읽어 새 줄을 만들고,
    틱톡·인스타그램에서 찾은 새 번호는 그 플랫폼 칸이 비어 있는 가장 오래된 줄에 넣는다(없으면 새 줄)."""
    changed = False
    def fill(key, value, title=None):
        nonlocal changed
        for cfg in reversed(videos):            # 목록은 최신이 앞이므로 뒤에서부터 = 오래된 것부터
            if cfg.get("auto") and not cfg.get(key):
                cfg[key] = value
                changed = True
                return
        kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        videos.insert(0, {"id": "v" + value[-8:], "title": title or "새 영상", "posted": f"{kst.month}월 {kst.day}일 {kst:%H:%M}", key: value, "auto": True})
        changed = True
    known = {k: {v.get(k) for v in videos} for k in ("youtube", "tiktok", "insta")}
    for vid in reversed(list(yt_ids)):          # Shorts 탭은 최신이 앞
        if vid in known["youtube"]:
            continue
        title, posted = None, None
        try:
            html = get(f"https://www.youtube.com/shorts/{vid}", {"Cookie": "CONSENT=YES+1; SOCS=CAI"})
            m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
            if m:
                title = re.split(r"\s+#", m.group(1).replace("&quot;", '"').replace("&amp;", "&"))[0].strip()[:40]
            m = re.search(r'"(?:publishDate|uploadDate)":"([^"]+)"', html)
            if m:
                t = datetime.datetime.fromisoformat(m.group(1)).astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                posted = f"{t.month}월 {t.day}일 {t:%H:%M}"
        except Exception as e:
            log.append(f"새 유튜브 영상 {vid} 정보 실패: {e}")
        kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        videos.insert(0, {"id": "v" + vid[-8:], "title": title or "새 영상", "posted": posted or f"{kst.month}월 {kst.day}일 {kst:%H:%M}", "youtube": vid, "auto": True})
        changed = True
        log.append(f"새 영상 등록(유튜브): {title or vid}")
    for tid in tt_ids or []:
        if tid in known["tiktok"]:
            continue
        # 틱톡에만 올리는 외국어판(지금은 중국어)은 원본과 따로 한 줄을 만든다: "한글 제목(중국)"
        desc = ""
        try:
            desc = tiktok_desc(tid)
        except Exception as e:
            log.append(f"틱톡 설명 읽기 실패 {tid}: {e}")
        is_zh = bool(re.search(r"[一-鿿]", desc)) and not re.search(r"[가-힣]", desc)
        if is_zh:
            base = next((v for v in videos if any(h in desc for h in v.get("zh_hint", []))), None)                 or next((v for v in videos if v.get("lang") != "zh"), None)
            kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
            videos.insert(0, {"id": "zh" + tid[-8:], "title": "(중국) " + (base["title"] if base else "새 영상"),
                              "posted": f"{kst.month}월 {kst.day}일 {kst:%H:%M}", "tiktok": tid, "lang": "zh"})
            changed = True
            log.append(f"새 영상 등록(틱톡 중국어판): {tid}")
        else:
            fill("tiktok", tid)
            log.append(f"새 영상 등록(틱톡): {tid}")
    for code in ig_codes or []:
        if code not in known["insta"]:
            fill("insta", code)
            log.append(f"새 영상 등록(인스타): {code}")
    if changed:
        json.dump(videos, open(os.path.join(HERE, "videos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return videos


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
    try:
        ig_codes = list(reversed([k for k in (ig or {}) if not k.startswith("__")]))  # 릴스 탭은 최신이 앞 → 오래된 것부터
        try:
            tt_new = tiktok_list({v.get("tiktok") for v in videos})
        except Exception as e:
            tt_new = None
            log.append(f"틱톡 목록 실패: {e}")
        videos = discover(videos, yt, tt_new, ig_codes, log)
    except Exception as e:
        log.append(f"새 영상 찾기 실패: {e}")
    snap_videos = []
    for cfg in videos:
        v = dict(prev.get(cfg["id"], {"tiktok": 0, "tt_likes": 0, "tt_comments": 0, "youtube": 0, "insta": 0}))
        v.update({"id": cfg["id"], "title": cfg["title"], "posted": cfg["posted"]})
        if yt.get(cfg.get("youtube")) is not None:
            v["youtube"] = yt[cfg["youtube"]]
        if cfg.get("youtube"):
            try:
                for k, val in youtube_video(cfg["youtube"]).items():
                    if val is not None:
                        v[k] = val
            except Exception as e:
                log.append(f"youtube {cfg['id']} 실패: {e}")
        if cfg.get("tiktok"):
            try:
                for k, val in tiktok(cfg["tiktok"]).items():
                    if val is not None:
                        v[k] = val
            except Exception as e:
                log.append(f"tiktok {cfg['id']} 실패: {e}")
        if ig and ig.get(cfg.get("insta")) is not None:
            for k, val in ig[cfg["insta"]].items():
                if val is not None:
                    v[k] = val
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
    snap = {"at": kst.strftime("%Y-%m-%d %H:%M"), "followers": followers, "insta_posts": posts, "videos": snap_videos}
    # 시청 지속 값(스튜디오 분석 화면에서 읽어 retention.json에 넣어 둔 것)을 기록에 얹는다
    try:
        ret = json.load(open(os.path.join(HERE, "retention.json"), encoding="utf-8"))
        snap["ret_at"] = ret.get("at")
        for v in snap_videos:
            v.update(ret.get("videos", {}).get(v["id"], {}))
    except Exception:
        pass
    data["snapshots"].append(snap)
    json.dump(data, open(os.path.join(HERE, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, "build.py")], check=True)
    print("저장:", kst.strftime("%H:%M"), {v["id"]: (v["tiktok"], v["youtube"], v.get("insta")) for v in snap_videos}, "|", "; ".join(log) or "오류 없음")


if __name__ == "__main__":
    main()
