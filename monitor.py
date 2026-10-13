# -*- coding: utf-8 -*-
"""PC에서 켜 두는 모니터링. 정해진 간격으로 유튜브·틱톡을 읽어 깃허브에 올린다.
실행: python monitor.py [간격(분), 기본 10]
깃허브 페이지는 한 시간에 10번쯤까지만 다시 만들어 주므로 간격을 6분보다 짧게 잡지 않는다.
인스타그램은 로그인이 있어야 읽혀서 여기서는 읽지 않는다(Claude가 크롬으로 읽어 apply.py로 넣는다)."""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
interval = max(6, int(sys.argv[1]) if len(sys.argv) > 1 else 10) * 60
git = lambda *a, **k: subprocess.run(["git", "-C", HERE, *a], **k)
while True:
    try:
        git("pull", "-q", "--rebase", check=False)
        subprocess.run([sys.executable, os.path.join(HERE, "crawl.py")], check=True)
        git("add", "-A")
        git("commit", "-q", "-m", "모니터링 갱신", check=False)
        git("push", "-q", check=False)
    except Exception as e:
        print("실패:", e, flush=True)
    sys.stdout.flush()
    time.sleep(interval)
