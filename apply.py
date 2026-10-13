# -*- coding: utf-8 -*-
"""손으로(또는 Claude가 크롬으로) 읽은 값을 data.json에 새 기록으로 덧붙인다. 주로 인스타그램 값에 쓴다.
실행: python apply.py '{"insta_posts":4,"followers":{"instagram":0},"videos":{"coin":{"insta":83}}}'
새 영상은 videos.json에 먼저 추가한다."""
import datetime, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
cfg = json.load(open(os.path.join(HERE, "videos.json"), encoding="utf-8"))
new = json.loads(sys.argv[1])
last = data["snapshots"][-1]
prev = {v["id"]: v for v in last["videos"]}
videos = []
for c in cfg:
    v = dict(prev.get(c["id"], {"tiktok": 0, "tt_likes": 0, "tt_comments": 0, "youtube": 0, "insta": 0}))
    v.update({"id": c["id"], "title": c["title"], "posted": c["posted"]})
    v.update(new.get("videos", {}).get(c["id"], {}))
    videos.append(v)
followers = dict(last["followers"])
followers.update(new.get("followers", {}))
snap = {"at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "followers": followers, "insta_posts": new.get("insta_posts", last.get("insta_posts", 0)), "videos": videos}
if new.get("ret_at") or last.get("ret_at"):
    snap["ret_at"] = new.get("ret_at") or last.get("ret_at")
data["snapshots"].append(snap)
json.dump(data, open(os.path.join(HERE, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, "build.py")], check=True)
print("snapshots:", len(data["snapshots"]), "at", snap["at"])
