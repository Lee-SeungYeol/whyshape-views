# -*- coding: utf-8 -*-
"""기록.json(조회 시점별 수치)을 읽어 조회수.html 한 장을 만든다.
실행: python 대시보드/만들기.py
수치는 Claude가 크롬으로 틱톡 스튜디오·유튜브 스튜디오·인스타그램을 읽어 기록.json에 덧붙인다."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))

HTML = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>왜이모양이야 조회수</title>
<style>
  :root {
    --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink2: #52514e; --line: #e4e3df;
    --tiktok: #2a78d6; --youtube: #eb6834; --insta: #1baf7a; --up: #0ca30c;
    --v1: #6250d6; --v2: #eda100; --v3: #e87ba4; --v4: #008300;
  }
  @media (prefers-color-scheme: dark) {
    :root { --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --line: #33332f;
      --tiktok: #3987e5; --youtube: #d95926; --insta: #199e70;
      --v1: #9085e9; --v2: #c98500; --v3: #d55181; --v4: #008300; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--page); color: var(--ink); font-family: "Malgun Gothic", "Segoe UI", sans-serif; }
  main { max-width: 1080px; margin: 0 auto; padding: 28px 20px 60px; }
  h1 { font-size: 26px; margin: 0 0 4px; }
  .sub { color: var(--ink2); font-size: 14px; margin-bottom: 22px; }
  .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 26px; }
  .tile { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; }
  .tile .k { font-size: 14px; color: var(--ink2); display: flex; align-items: center; gap: 8px; }
  .tile .v { font-size: 38px; font-weight: 700; line-height: 1.15; margin-top: 6px; font-variant-numeric: tabular-nums; }
  .tile .d { font-size: 13px; color: var(--ink2); margin-top: 4px; }
  .dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
  .card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 18px; margin-bottom: 22px; }
  h2 { font-size: 18px; margin: 0 0 4px; }
  .note { color: var(--ink2); font-size: 13px; margin-bottom: 14px; }
  .legend { display: flex; gap: 18px; font-size: 13px; color: var(--ink2); margin-bottom: 12px; }
  .legend span { display: inline-flex; align-items: center; gap: 6px; }
  .row { display: grid; grid-template-columns: minmax(150px, 280px) 1fr 70px; gap: 12px; align-items: center; padding: 9px 0; border-top: 1px solid var(--line); }
  .row:first-of-type { border-top: 0; }
  .name { font-size: 15px; font-weight: 700; }
  .when { font-size: 12px; color: var(--ink2); font-weight: 400; }
  .bar { display: flex; gap: 2px; height: 22px; }
  .seg { height: 100%; border-radius: 4px; min-width: 2px; position: relative; }
  .seg:hover { outline: 2px solid var(--ink); outline-offset: 1px; }
  .tot { text-align: right; font-weight: 700; font-variant-numeric: tabular-nums; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th, td { padding: 9px 8px; border-top: 1px solid var(--line); text-align: right; font-variant-numeric: tabular-nums; }
  th { color: var(--ink2); font-weight: 400; border-top: 0; }
  th:first-child, td:first-child { text-align: left; }
  tbody tr:hover { background: color-mix(in srgb, var(--ink) 5%, transparent); }
  tr.total td { font-weight: 700; border-top: 2px solid var(--ink2); background: color-mix(in srgb, var(--ink) 5%, transparent); }
  .plus { color: var(--up); font-size: 12px; margin-left: 4px; }
  .muted { color: var(--ink2); }
  .prow { display: grid; grid-template-columns: 110px 1fr 250px; gap: 12px; align-items: center; padding: 8px 0; border-top: 1px solid var(--line); }
  .prow:first-child { border-top: 0; }
  .pname { font-weight: 700; font-size: 15px; display: flex; align-items: center; gap: 8px; }
  .ptrack { height: 22px; background: color-mix(in srgb, var(--ink) 6%, transparent); border-radius: 4px; }
  .pfill { height: 100%; border-radius: 4px; min-width: 2px; }
  .pinfo { font-size: 13px; color: var(--ink2); text-align: right; }
  .pinfo b { color: var(--ink); font-size: 15px; }
  .hm { display: grid; gap: 6px; align-items: center; font-size: 14px; }
  .hm .hh { color: var(--ink2); font-size: 13px; }
  .cell { display: flex; align-items: center; gap: 8px; font-variant-numeric: tabular-nums; }
  .sw { width: 34px; height: 22px; border-radius: 4px; border: 1px solid var(--line); flex: none; }
  .minis { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; }
  .mini { border: 1px solid var(--line); border-radius: 12px; padding: 12px 12px 4px; }
  .mt { font-size: 14px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .rk { display: inline-block; min-width: 22px; height: 22px; line-height: 22px; text-align: center; border-radius: 6px; background: var(--line); font-size: 12px; margin-right: 8px; }
  .mv { font-size: 26px; font-weight: 700; font-variant-numeric: tabular-nums; margin: 2px 0 2px; }
  .mv .plus { font-size: 13px; }
  .hrow { display: grid; grid-template-columns: minmax(150px, 300px) 1fr 190px; gap: 14px; align-items: center; padding: 10px 0; border-top: 1px solid var(--line); }
  .hrow:first-child { border-top: 0; }
  .hname { font-weight: 700; font-size: 15px; display: flex; align-items: center; }
  .lv { flex: none; margin-left: 8px; font-size: 12px; font-weight: 700; padding: 2px 9px; border-radius: 999px; border: 1px solid var(--line); white-space: nowrap; }
  .lv.s3 { background: var(--up); border-color: var(--up); color: var(--surface); }
  .lv.s2 { border-color: var(--up); color: var(--up); }
  .lv.s1 { color: var(--ink2); }
  .hnum { text-align: right; line-height: 1.2; }
  .hnum b { font-size: 26px; font-variant-numeric: tabular-nums; }
  .hnum small { font-size: 12px; color: var(--ink2); margin-left: 4px; }
  .hup { color: var(--up); }
  .hflow { display: block; font-size: 12px; color: var(--ink2); margin-top: 2px; }
  .hflow.on { color: var(--up); }
  .rrow { padding: 12px 0; border-top: 1px solid var(--line); }
  .rrow:first-child { border-top: 0; }
  .rname { font-weight: 700; font-size: 15px; margin-bottom: 6px; }
  .rline { display: grid; grid-template-columns: 76px minmax(80px, 1fr) 190px 150px 170px; gap: 12px; align-items: center; padding: 3px 0; }
  .rp { font-size: 13px; color: var(--ink2); display: flex; align-items: center; gap: 6px; }
  .rinfo { font-size: 13px; color: var(--ink2); }
  .rinfo b { color: var(--ink); font-size: 15px; }
  .rline .ptrack { height: 14px; }
  svg text { font-family: inherit; fill: var(--ink2); font-size: 12px; }
  svg .lab { fill: var(--ink); font-size: 13px; font-weight: 700; }
  .legend { flex-wrap: wrap; row-gap: 6px; }
  #heat { overflow-x: auto; }
  @media (max-width: 640px) {
    main { padding: 18px 12px 48px; }
    h1 { font-size: 22px; }
    h2 { font-size: 17px; }
    .sub { font-size: 12px; }
    .tiles { grid-template-columns: 1fr 1fr; gap: 10px; }
    .tile { padding: 12px 12px; }
    .tile .k { font-size: 12px; }
    .tile .v { font-size: 28px; }
    .tile .d { font-size: 11px; }
    .card { padding: 14px 12px; border-radius: 12px; }
    .note { font-size: 12px; }
    .row { grid-template-columns: 1fr 58px; row-gap: 6px; }
    .row .name { grid-column: 1 / -1; font-size: 14px; }
    .prow { grid-template-columns: 1fr !important; row-gap: 6px; }
    .rline { grid-template-columns: 62px 1fr; row-gap: 2px; }
    .rline .rinfo { grid-column: 2; }
    .hrow { grid-template-columns: 1fr 104px; column-gap: 10px; row-gap: 4px; }
    .hname { grid-column: 1 / -1; font-size: 14px; }
    .hnum b { font-size: 22px; }
    .pinfo { text-align: left; }
    .hm { min-width: 520px; font-size: 13px; }
    .minis { grid-template-columns: 1fr; }
    .mv { font-size: 22px; }
    table { font-size: 13px; }
    th, td { padding: 8px 6px; }
  }
  #tip { position: fixed; pointer-events: none; background: var(--ink); color: var(--surface); font-size: 13px; padding: 6px 10px; border-radius: 8px; display: none; z-index: 5; white-space: nowrap; }
  a { color: inherit; }
</style>
</head>
<body>
<main>
  <h1>왜이모양이야 조회수</h1>
  <div class="sub" id="sub"></div>
  <div class="tiles" id="tiles"></div>
  <div class="card">
    <h2>전체 조회수 추세</h2>
    <div class="note">모든 영상의 조회수를 합친 값이 시간에 따라 어떻게 늘었는지 보여 줍니다. 굵은 줄이 세 곳을 합친 전체이고, 가는 줄이 플랫폼별입니다. 새 영상이 목록에 들어온 때에는 그만큼 올라갑니다.</div>
    <div class="legend"><span><i class="dot" style="background:var(--ink)"></i>전체</span><span><i class="dot" style="background:var(--tiktok)"></i>틱톡</span><span><i class="dot" style="background:var(--youtube)"></i>유튜브</span><span><i class="dot" style="background:var(--insta)"></i>인스타그램</span></div>
    <div id="totals"></div>
  </div>
  <div class="card">
    <h2>영상별 조회수 (상위 10개)</h2>
    <div class="note">틱톡, 유튜브, 인스타그램을 합친 길이입니다. 막대에 마우스를 올리면 숫자가 나옵니다.</div>
    <div class="legend"><span><i class="dot" style="background:var(--tiktok)"></i>틱톡</span><span><i class="dot" style="background:var(--youtube)"></i>유튜브</span><span><i class="dot" style="background:var(--insta)"></i>인스타그램</span></div>
    <div id="bars"></div>
  </div>
  <div class="card">
    <h2>구독자·팔로워 변화</h2>
    <div class="note">세 곳의 구독자와 팔로워 수가 시간에 따라 어떻게 바뀌었는지 보여 줍니다. 마우스를 올리면 그때의 숫자가 나옵니다.</div>
    <div class="legend"><span><i class="dot" style="background:var(--tiktok)"></i>틱톡 팔로워</span><span><i class="dot" style="background:var(--youtube)"></i>유튜브 구독자</span><span><i class="dot" style="background:var(--insta)"></i>인스타그램 팔로워</span></div>
    <div id="foll"></div>
  </div>
  <div class="card">
    <h2>지금 오르는 영상</h2>
    <div class="note">최근 1시간에 조회수가 많이 늘어난 순서입니다. 큰 숫자는 1시간에 늘어난 조회수, 가운데 줄은 최근 3시간의 오름세입니다(가파를수록 빨리 오르는 중). 세기는 1시간에 200회 이상이면 강세, 30회 이상이면 보통, 그보다 적으면 약함입니다.</div>
    <div id="hot"></div>
  </div>
  <div class="card">
    <h2>시간대별 조회수 (하루 24시간)</h2>
    <div class="note" id="hoursnote"></div>
    <div id="hours"></div>
  </div>
  <div class="card">
    <h2>틱톡 시간대별 조회수 (하루 24시간)</h2>
    <div class="note" id="hoursnote_tt"></div>
    <div id="hours_tt"></div>
  </div>
  <div class="card">
    <h2>플랫폼별 세기</h2>
    <div class="note">어느 플랫폼에서 조회수가 많이 나오는지, 영상마다 어디서 강한지 보여 줍니다. 아래 표의 네모는 진할수록 조회수가 많다는 뜻입니다.</div>
    <div id="plat"></div>
    <div id="heat" style="margin-top:18px"></div>
  </div>
  <div class="card">
    <h2>조회수 변화 (상위 10개)</h2>
    <div class="note">조회수가 많은 순서로 10개까지, 영상마다 세 곳을 합친 조회수가 어떻게 늘었는지 보여 줍니다. 기록은 날짜가 바뀌어도 계속 이어지고, 큰 숫자 옆 초록색은 최근 24시간 동안 늘어난 양입니다. 그래프마다 세로 눈금이 다릅니다.</div>
    <div id="line" class="minis"></div>
  </div>
  <div class="card">
    <h2>틱톡 조회수 변화 (상위 10개)</h2>
    <div class="note">틱톡 조회수만 따로 본 것입니다. 틱톡 조회수가 많은 순서로 10개까지이고, 큰 숫자 옆 초록색은 최근 24시간 동안 늘어난 양입니다. 그래프마다 세로 눈금이 다릅니다.</div>
    <div id="line_tt" class="minis"></div>
  </div>
  <div class="card">
    <h2>자세한 숫자</h2>
    <div class="note" id="tnote"></div>
    <div style="overflow-x:auto"><table style="min-width:980px"><thead><tr><th>영상</th><th>올린 때</th><th>틱톡 조회</th><th>틱톡 좋아요</th><th>틱톡 댓글</th><th>유튜브 조회</th><th>유튜브 좋아요</th><th>유튜브 댓글</th><th>인스타 조회</th><th>인스타 좋아요</th><th>인스타 댓글</th><th>합계</th></tr></thead><tbody id="tb"></tbody></table></div>
  </div>
</main>
<div id="tip"></div>
<script>
const EMBED = __DATA__;
function render(DATA) {
const snaps = DATA.snapshots, now = snaps[snaps.length - 1];
// 초록색 증가 숫자의 기준: 바로 앞 기록(크롤러가 3분마다 읽으므로 최근 3분 동안 늘어난 양. 사용자 요청 2026-10-13)
const prev = snaps.length > 1 ? snaps[snaps.length - 2] : null;
const tot = (v) => (v.tiktok || 0) + (v.youtube || 0) + (v.insta || 0);
const n = (x) => (x == null ? "–" : x.toLocaleString("ko-KR"));
const prevOf = (id) => (prev ? prev.videos.find((v) => v.id === id) : null);
const plus = (a, b) => (b != null && a != null && a - b > 0 ? `<span class="plus">+${n(a - b)}</span>` : "");
const sum = (k) => now.videos.reduce((s, v) => s + (v[k] || 0), 0);
const psum = (k) => (prev ? prev.videos.reduce((s, v) => s + (v[k] || 0), 0) : null);
document.getElementById("sub").textContent = `마지막으로 읽은 때: ${now.at}` + (prev ? ` · 초록색 숫자는 최근 3분 증가분` : "") + " · 크롤러가 3분마다 읽고, 이 화면은 1분마다 새 값을 확인합니다(최대 4분쯤 늦을 수 있음).";
const tiles = [
  ["전체 조회수", sum("tiktok") + sum("youtube") + sum("insta"), prev ? psum("tiktok") + psum("youtube") + psum("insta") : null, null, "틱톡 + 유튜브 + 인스타그램"],
  ["틱톡 조회수", sum("tiktok"), psum("tiktok"), "var(--tiktok)", `팔로워 ${n(now.followers.tiktok)}`],
  ["유튜브 조회수", sum("youtube"), psum("youtube"), "var(--youtube)", `구독자 ${n(now.followers.youtube)}`],
  ["인스타그램 조회수", sum("insta"), psum("insta"), "var(--insta)", `팔로워 ${n(now.followers.instagram)} · 게시물 ${n(now.insta_posts)}`],
];
document.getElementById("tiles").innerHTML = tiles.map(([k, v, p, c, d]) => `<div class="tile"><div class="k">${c ? `<i class="dot" style="background:${c}"></i>` : ""}${k}</div><div class="v">${n(v)}</div><div class="d">${p != null && v - p > 0 ? `<span class="plus" style="margin-left:0">+${n(v - p)}</span> · ` : ""}${d}</div></div>`).join("");
const max = Math.max(1, ...now.videos.map(tot));
const ranked = [...now.videos].sort((a, b) => tot(b) - tot(a)).slice(0, 10);
document.getElementById("bars").innerHTML = ranked.map((v) => {
  const t = v.tiktok || 0, y = v.youtube || 0, g = v.insta || 0;
  const seg = (val, color, label) => (val > 0 ? `<div class="seg" style="width:${(val / max) * 100}%;background:${color}" data-tip="${label} ${n(val)}회"></div>` : "");
  return `<div class="row"><div class="name">${v.title}<div class="when">${v.posted}</div></div><div class="bar">${seg(t, "var(--tiktok)", "틱톡")}${seg(y, "var(--youtube)", "유튜브")}${seg(g, "var(--insta)", "인스타그램")}</div><div class="tot">${n(t + y + g)}</div></div>`;
}).join("");
document.getElementById("tnote").textContent = prev ? `초록색 숫자는 바로 앞 기록(${prev.at.slice(11)}) 이후, 약 3분 동안 늘어난 양입니다. 늘지 않았으면 표시되지 않습니다.` : "";
document.getElementById("tb").innerHTML = ranked.map((v) => {
  const p = prevOf(v.id) || {};
  return `<tr><td>${v.title}</td><td class="muted">${v.posted}</td><td>${n(v.tiktok)}${plus(v.tiktok, p.tiktok)}</td><td>${n(v.tt_likes)}</td><td>${n(v.tt_comments)}</td><td>${n(v.youtube)}${plus(v.youtube, p.youtube)}</td><td>${n(v.yt_likes)}</td><td>${n(v.yt_comments)}</td><td class="${v.insta == null ? "muted" : ""}">${v.insta == null ? "못 읽음" : n(v.insta) + plus(v.insta, p.insta)}</td><td>${n(v.ig_likes)}</td><td>${n(v.ig_comments)}</td><td><b>${n((v.tiktok || 0) + (v.youtube || 0) + (v.insta || 0))}</b></td></tr>`;
}).join("") + (() => {
  const K = ["tiktok", "tt_likes", "tt_comments", "youtube", "yt_likes", "yt_comments", "insta", "ig_likes", "ig_comments"];
  const all = sum("tiktok") + sum("youtube") + sum("insta");
  return `<tr class="total"><td>합계</td><td></td>${K.map((k) => `<td>${n(sum(k))}</td>`).join("")}<td>${n(all)}</td></tr>`;
})();
// ---- 전체 조회수 추세: 합계(굵게)와 플랫폼별(가늘게) ----
(() => {
  const T = (s) => new Date(s.at.replace(" ", "T")).getTime();
  const S = [["all", "전체", "var(--ink)", 3], ["tiktok", "틱톡", "var(--tiktok)", 2], ["youtube", "유튜브", "var(--youtube)", 2], ["insta", "인스타그램", "var(--insta)", 2]];
  const val = (s, k) => s.videos.reduce((a, v) => a + (k === "all" ? tot(v) : v[k] || 0), 0);
  const t0 = T(snaps[0]), t1 = Math.max(T(now), t0 + 60000);
  const W = Math.max(330, Math.min(1000, document.getElementById("totals").clientWidth || 1000)), H = W < 600 ? 250 : 300, L = W < 600 ? 44 : 56, R = W < 600 ? 112 : 160, TOP = 14, B = 30;
  const ymax = Math.max(10, ...snaps.map((s) => val(s, "all"))) * 1.08;
  const X = (t) => L + ((t - t0) / (t1 - t0)) * (W - L - R), Y = (y) => TOP + (1 - y / ymax) * (H - TOP - B);
  const hh = (t) => { const d = new Date(t); return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`; };
  const p10 = Math.pow(10, Math.floor(Math.log10(ymax))), step = ymax / p10 < 2.5 ? p10 / 2 : p10;
  let g = "";
  for (let y = 0; y <= ymax; y += step) g += `<line x1="${L}" x2="${W - R}" y1="${Y(y)}" y2="${Y(y)}" stroke="var(--line)"/><text x="${L - 8}" y="${Y(y) + 4}" text-anchor="end">${n(y)}</text>`;
  for (let d = new Date(t0); d.getTime() <= t1; d = new Date(d.getTime() + 86400000)) { const m = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1).getTime(); if (m < t1) g += `<line x1="${X(m)}" x2="${X(m)}" y1="${TOP}" y2="${H - B}" stroke="var(--line)"/><text x="${X(m) + 3}" y="${TOP + 10}">${new Date(m).getMonth() + 1}/${new Date(m).getDate()}</text>`; }
  g += `<text x="${L}" y="${H - 8}">${hh(t0)}</text><text x="${W - R}" y="${H - 8}" text-anchor="end">${hh(t1)}</text>`;
  const ends = S.map(([k, name, color]) => ({ k, name, v: val(now, k) })).map((e) => ({ ...e, y: Y(e.v) })).sort((a, b) => b.y - a.y);
  for (let i = 1; i < ends.length; i++) if (ends[i - 1].y - ends[i].y < 17) ends[i].y = ends[i - 1].y - 17;
  S.forEach(([k, name, color, w]) => {
    const pts = snaps.map((s) => ({ t: T(s), at: s.at, y: val(s, k) }));
    g += `<polyline fill="none" stroke="${color}" stroke-width="${w}" stroke-linejoin="round" points="${pts.map((p) => X(p.t) + "," + Y(p.y)).join(" ")}"/>`;
    const last = pts[pts.length - 1];
    g += `<circle cx="${X(last.t)}" cy="${Y(last.y)}" r="4" fill="${color}" stroke="var(--surface)" stroke-width="2"/>`;
    if (k === "all") pts.forEach((p) => { g += `<rect x="${X(p.t) - 5}" y="${TOP}" width="10" height="${H - TOP - B}" fill="transparent" data-tip="${p.at.slice(5)} · 전체 ${n(p.y)}회"/>`; });
    const e = ends.find((x) => x.k === k);
    g += `<text class="lab" x="${W - R + 8}" y="${e.y + 4}">${W < 600 ? name.replace("인스타그램", "인스타") : name} ${n(e.v)}</text>`;
  });
  document.getElementById("totals").innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="전체 조회수의 시간 변화">${g}</svg>`;
})();
// ---- 구독자·팔로워 변화: 세 줄 꺾은선 ----
(() => {
  const T = (s) => new Date(s.at.replace(" ", "T")).getTime();
  const P = [["tiktok", "틱톡", "var(--tiktok)"], ["youtube", "유튜브", "var(--youtube)"], ["instagram", "인스타그램", "var(--insta)"]];
  const t0 = T(snaps[0]), t1 = Math.max(T(now), t0 + 60000);
  const W = Math.max(330, Math.min(1000, document.getElementById("foll").clientWidth || 1000)), H = W < 600 ? 220 : 260, L = W < 600 ? 34 : 46, R = W < 600 ? 108 : 150, TOP = 14, B = 30;
  const ymax = Math.max(4, ...snaps.flatMap((s) => P.map(([k]) => (s.followers || {})[k] || 0))) * 1.15;
  const X = (t) => L + ((t - t0) / (t1 - t0)) * (W - L - R), Y = (y) => TOP + (1 - y / ymax) * (H - TOP - B);
  const hh = (t) => { const d = new Date(t); return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`; };
  const step = Math.max(1, Math.ceil(ymax / 4 / Math.pow(10, Math.floor(Math.log10(ymax / 4)))) * Math.pow(10, Math.floor(Math.log10(ymax / 4))));
  let g = "";
  for (let y = 0; y <= ymax; y += step) g += `<line x1="${L}" x2="${W - R}" y1="${Y(y)}" y2="${Y(y)}" stroke="var(--line)"/><text x="${L - 8}" y="${Y(y) + 4}" text-anchor="end">${n(y)}</text>`;
  for (let d = new Date(t0); d.getTime() <= t1; d = new Date(d.getTime() + 86400000)) { const m = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1).getTime(); if (m < t1) g += `<line x1="${X(m)}" x2="${X(m)}" y1="${TOP}" y2="${H - B}" stroke="var(--line)"/><text x="${X(m) + 3}" y="${TOP + 10}">${new Date(m).getMonth() + 1}/${new Date(m).getDate()}</text>`; }
  g += `<text x="${L}" y="${H - 8}">${hh(t0)}</text><text x="${W - R}" y="${H - 8}" text-anchor="end">${hh(t1)}</text>`;
  const ends = P.map(([k, name, color]) => ({ k, name, color, v: (now.followers || {})[k] || 0 })).map((e) => ({ ...e, y: Y(e.v) })).sort((a, b) => b.y - a.y);
  for (let i = 1; i < ends.length; i++) if (ends[i - 1].y - ends[i].y < 17) ends[i].y = ends[i - 1].y - 17;
  P.forEach(([k, name, color]) => {
    const pts = snaps.map((s) => ({ t: T(s), at: s.at, y: (s.followers || {})[k] || 0 }));
    g += `<polyline fill="none" stroke="${color}" stroke-width="2" stroke-linejoin="round" points="${pts.map((p) => X(p.t) + "," + Y(p.y)).join(" ")}"/>`;
    const last = pts[pts.length - 1];
    g += `<circle cx="${X(last.t)}" cy="${Y(last.y)}" r="4" fill="${color}" stroke="var(--surface)" stroke-width="2"/>`;
    pts.forEach((p) => { g += `<rect x="${X(p.t) - 5}" y="${Y(p.y) - 9}" width="10" height="18" fill="transparent" data-tip="${name} · ${p.at.slice(5)} · ${n(p.y)}명"/>`; });
    const e = ends.find((x) => x.k === k);
    g += `<text class="lab" x="${W - R + 8}" y="${e.y + 4}">${W < 600 ? name.replace("인스타그램", "인스타") : name} ${n(e.v)}</text>`;
  });
  document.getElementById("foll").innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="구독자와 팔로워 수의 변화">${g}</svg>`;
})();
// ---- 지금 오르는 영상: 최근 1시간 증가량과 그 전 1시간 대비 흐름 ----
(() => {
  const T = (s) => new Date(s.at.replace(" ", "T")).getTime(), H = 3600000, tn = T(now);
  const at = (id, t) => { let best = null; for (const s of snaps) { if (T(s) <= t) { const v = s.videos.find((q) => q.id === id); if (v) best = { t: T(s), y: tot(v) }; } } return best; };
  const first = (id) => { for (const s of snaps) { const v = s.videos.find((q) => q.id === id); if (v) return { t: T(s), y: tot(v) }; } return null; };
  const rows = now.videos.map((v) => {
    const cur = tot(v), a = at(v.id, tn - H) || first(v.id), b = at(v.id, tn - 2 * H);
    const span = Math.max((tn - a.t) / H, 1), rate = (cur - a.y) / span;              // 최근 1시간에 실제로 늘어난 양. 기록이 1시간보다 짧아도 부풀려 환산하지 않는다(5분에 1회를 시간당 12회로 보이게 했던 문제)
    const prevRate = b && a.t > b.t ? (a.y - b.y) / ((a.t - b.t) / H) : null;
    let flow = "지켜보는 중", cls = "muted";
    if (rate <= 0) { flow = "멈춤"; }
    else if (prevRate == null) { flow = "오르는 중"; cls = "up"; }
    else if (rate > prevRate * 1.2) { flow = "더 빨라짐"; cls = "up"; }
    else if (rate < prevRate * 0.6) { flow = "느려짐"; }
    else { flow = "꾸준히 오름"; cls = "up"; }
    return { v, rate, flow, cls, cur };
  }).sort((x, y) => y.rate - x.rate).slice(0, 10);
  // 영상마다 최근 3시간 동안 늘어난 양을 작은 꺾은선으로 그린다. 세로 눈금은 모든 영상이 같아서 가파를수록 빨리 오르는 것이다.
  const SPAN = 3 * H, t0 = tn - SPAN, SW = 220, SH = 46;
  const series = rows.map((r) => {
    const pts = snaps.filter((s) => T(s) >= t0).map((s) => { const v = s.videos.find((q) => q.id === r.v.id); return v ? { t: T(s), y: tot(v) } : null; }).filter(Boolean);
    const base = pts.length ? pts[0].y : r.cur;
    return pts.map((q) => ({ t: q.t, y: q.y - base }));
  });
  const gmax = Math.max(1, ...series.flatMap((p) => p.map((q) => q.y)));
  const spark = (pts, on) => {
    if (pts.length < 2) return `<svg viewBox="0 0 ${SW} ${SH}" width="100%" height="${SH}"></svg>`;
    const X = (t) => 4 + ((t - t0) / SPAN) * (SW - 8), Y = (y) => SH - 5 - (y / gmax) * (SH - 10);
    const line = pts.map((q) => X(q.t).toFixed(1) + "," + Y(q.y).toFixed(1)).join(" "), last = pts[pts.length - 1];
    const color = on ? "var(--up)" : "var(--ink2)";
    return `<svg viewBox="0 0 ${SW} ${SH}" width="100%" height="${SH}" preserveAspectRatio="none" role="img" aria-label="최근 3시간 증가"><line x1="4" x2="${SW - 4}" y1="${SH - 5}" y2="${SH - 5}" stroke="var(--line)"/><polygon points="${X(pts[0].t).toFixed(1)},${SH - 5} ${line} ${X(last.t).toFixed(1)},${SH - 5}" fill="${color}" opacity="0.14"/><polyline fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round" vector-effect="non-scaling-stroke" points="${line}"/></svg>`;
  };
  document.getElementById("hot").innerHTML = rows.map((r, i) => {
    const on = r.rate > 0, gain = series[i].length ? series[i][series[i].length - 1].y : 0;
    const lv = r.rate >= 200 ? ["강세", "s3"] : r.rate >= 30 ? ["보통", "s2"] : ["약함", "s1"];
    return `<div class="hrow"><div class="hname"><span class="rk">${i + 1}</span><span>${r.v.title}</span><span class="lv ${lv[1]}">${lv[0]}</span></div><div class="hspark" data-tip="${r.v.title} · 최근 3시간 +${n(gain)}회">${spark(series[i], on)}</div><div class="hnum"><b class="${on ? "hup" : "muted"}">${on ? "+" + n(Math.round(r.rate)) : "0"}</b><small>회/시간</small><span class="hflow ${r.cls === "up" ? "on" : ""}">${r.flow}</span></div></div>`;
  }).join("");
})();
// ---- 시간대별 조회수: 0~23시마다 그 한 시간 동안 늘어난 조회수(세 플랫폼 합계). 여러 날이 쌓이면 하루 평균 ----
const hoursChart = (el, noteEl, val, color, lead) => {
  const T = (x) => new Date(x.at.replace(" ", "T"));
  const cell = {};                       // "날짜|시" → 그 시간에 늘어난 조회수
  for (let i = 1; i < snaps.length; i++) {
    const a = snaps[i - 1], b = snaps[i], tb = T(b);
    if (tb - T(a) > 2 * 3600000) continue;          // 기록이 오래 끊긴 구간은 어느 시간에 늘었는지 알 수 없어 뺀다
    const pa = Object.fromEntries(a.videos.map((v) => [v.id, v]));
    let d = 0;
    for (const v of b.videos) { const q = pa[v.id]; if (q) d += Math.max(0, val(v) - val(q)); }   // 새로 등록된 영상의 첫 값은 뺀다
    const k = `${tb.getFullYear()}-${tb.getMonth()}-${tb.getDate()}|${tb.getHours()}`;
    cell[k] = (cell[k] || 0) + d;
  }
  const sumH = Array(24).fill(0), cntH = Array(24).fill(0);
  for (const k in cell) { const h = +k.split("|")[1]; sumH[h] += cell[k]; cntH[h] += 1; }
  const avg = sumH.map((x, h) => (cntH[h] ? x / cntH[h] : null));
  const days = Math.max(0, ...cntH), mx = Math.max(1, ...avg.map((x) => x || 0));
  const best = avg.indexOf(Math.max(...avg.map((x) => x ?? -1)));
  const W = Math.max(330, Math.min(1000, document.getElementById(el).clientWidth || 1000)), H = W < 600 ? 230 : 270, L = W < 600 ? 40 : 52, R = 10, TOP = 26, B = 34;
  const bw = (W - L - R) / 24, Y = (y) => TOP + (1 - y / (mx * 1.08)) * (H - TOP - B);
  const p10 = Math.pow(10, Math.floor(Math.log10(mx))), step = mx / p10 < 2.5 ? p10 / 2 : p10;
  let g = "";
  for (let y = 0; y <= mx * 1.08; y += step) g += `<line x1="${L}" x2="${W - R}" y1="${Y(y)}" y2="${Y(y)}" stroke="var(--line)"/><text x="${L - 8}" y="${Y(y) + 4}" text-anchor="end">${n(Math.round(y))}</text>`;
  avg.forEach((v, h) => {
    const x = L + h * bw + 2, w = Math.max(2, bw - 4);
    if (v == null) g += `<rect x="${x}" y="${H - B - 3}" width="${w}" height="3" rx="1.5" fill="var(--line)" data-tip="${h}시 · 아직 기록 없음"/>`;
    else {
      const y = Y(v), hgt = Math.max(2, H - B - y);
      g += `<path d="M${x},${H - B} V${y + Math.min(4, hgt)} Q${x},${y} ${x + Math.min(4, w / 2)},${y} H${x + w - Math.min(4, w / 2)} Q${x + w},${y} ${x + w},${y + Math.min(4, hgt)} V${H - B} Z" fill="${h === best ? "var(--up)" : color}" data-tip="${h}시~${h + 1}시 · +${n(Math.round(v))}회${cntH[h] > 1 ? " (" + cntH[h] + "일 평균)" : ""}"/>`;
      if (h === best) g += `<text class="lab" x="${Math.min(W - R - 4, Math.max(L + 30, x + w / 2))}" y="${y - 7}" text-anchor="middle">+${n(Math.round(v))}</text>`;
    }
    if (h % (W < 600 ? 3 : 2) === 0) g += `<text x="${x + w / 2}" y="${H - B + 16}" text-anchor="middle">${h}</text>`;
  });
  g += `<text x="${W - R}" y="${H - 4}" text-anchor="end">시(한국 시각)</text>`;
  document.getElementById(el).innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="시간대별로 늘어난 조회수">${g}</svg>`;
  document.getElementById(noteEl).textContent = lead + " 하루 중 몇 시에 조회수가 많이 늘었는지 보여 줍니다. 막대 하나가 그 한 시간 동안 늘어난 조회수이고" + (days > 1 ? ", 여러 날의 평균입니다" : "") + ". 초록색이 가장 많이 오른 시간대입니다" + (best >= 0 && avg[best] != null ? `(${best}시~${best + 1}시)` : "") + ". 기록이 없는 시간대는 납작한 회색 줄로 나오며, 날이 지날수록 채워집니다.";
};
hoursChart("hours", "hoursnote", tot, "var(--v1)", "틱톡·유튜브·인스타그램을 합쳐,");
hoursChart("hours_tt", "hoursnote_tt", (v) => v.tiktok || 0, "var(--tiktok)", "틱톡 조회수만 따로,");
// ---- 플랫폼별 세기: 점유율 막대 + 영상×플랫폼 표 ----
(() => {
  const P = [["tiktok", "틱톡", "var(--tiktok)"], ["youtube", "유튜브", "var(--youtube)"], ["insta", "인스타그램", "var(--insta)"]];
  const all = P.reduce((a, [k]) => a + sum(k), 0) || 1;
  document.getElementById("plat").innerHTML = P.map(([k, name, color]) => {
    const total = sum(k), share = (total / all) * 100, posted = now.videos.filter((v) => v[k] != null).length || 1;
    const best = [...now.videos].sort((a, b) => (b[k] || 0) - (a[k] || 0))[0];
    return `<div class="prow"><div class="pname"><i class="dot" style="background:${color}"></i>${name}</div><div class="ptrack"><div class="pfill" style="width:${share}%;background:${color}" data-tip="${name} ${n(total)}회 · 전체의 ${share.toFixed(0)}%"></div></div><div class="pinfo"><b>${share.toFixed(0)}%</b> · 영상당 평균 ${n(Math.round(total / posted))}회<br>가장 잘된 영상: ${best.title} (${n(best[k] || 0)})</div></div>`;
  }).join("");
  // 진하기: 한 가지 색(파랑)의 밝은 단계에서 어두운 단계로
  const ramp = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"];
  const top = [...now.videos].sort((a, b) => tot(b) - tot(a)).slice(0, 10);
  const mx = Math.max(1, ...top.flatMap((v) => P.map(([k]) => v[k] || 0)));
  const sw = (val) => (val > 0 ? ramp[Math.min(ramp.length - 1, Math.floor(Math.sqrt(val / mx) * ramp.length))] : "transparent");
  let h = `<div class="hm" style="grid-template-columns: minmax(150px, 1.6fr) repeat(3, 1fr) 1.3fr"><div class="hh">영상</div>${P.map(([, name]) => `<div class="hh">${name}</div>`).join("")}<div class="hh">가장 강한 곳</div>`;
  top.forEach((v) => {
    const strong = [...P].sort((a, b) => (v[b[0]] || 0) - (v[a[0]] || 0))[0];
    h += `<div><b>${v.title}</b></div>` + P.map(([k, name]) => `<div class="cell" data-tip="${v.title} · ${name} ${n(v[k] || 0)}회"><i class="sw" style="background:${sw(v[k] || 0)}"></i>${n(v[k] || 0)}</div>`).join("") + `<div class="cell">${tot(v) > 0 ? `<i class="dot" style="background:${strong[2]}"></i>${strong[1]} ${Math.round(((v[strong[0]] || 0) / tot(v)) * 100)}%` : "–"}</div>`;
  });
  document.getElementById("heat").innerHTML = h + "</div>";
})();
// ---- 꺾은선: 조회수 상위 10개 영상을 작은 그래프 하나씩으로. 기록이 쌓이는 동안 날짜가 바뀌어도 계속 이어진다 ----
const minis = (el, val, color) => {
  const T = (s) => new Date(s.at.replace(" ", "T")).getTime();
  const t0 = T(snaps[0]), t1 = Math.max(T(now), t0 + 60000);
  const hh = (t) => { const d = new Date(t); return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`; };
  const top = [...now.videos].sort((a, b) => val(b) - val(a)).slice(0, 10);
  const W = Math.max(280, Math.min(460, (document.getElementById(el).clientWidth || 460) - 26)), H = 150, L = 8, R = 8, TOP = 10, B = 22;
  const dayAgo = T(now) - 24 * 3600 * 1000;
  document.getElementById(el).innerHTML = top.map((v, rank) => {
    const pts = snaps.map((s) => { const x = s.videos.find((q) => q.id === v.id); return x ? { t: T(s), at: s.at, y: val(x) } : null; }).filter(Boolean);
    const last = pts[pts.length - 1], ymax = Math.max(5, last.y, ...pts.map((p) => p.y)) * 1.1, ymin = 0;
    const X = (t) => L + ((t - t0) / (t1 - t0)) * (W - L - R), Y = (y) => TOP + (1 - (y - ymin) / (ymax - ymin)) * (H - TOP - B);
    const base = [...pts].reverse().find((p) => p.t <= dayAgo) || pts[0];
    const gain = last.y - base.y;
    // 날짜가 바뀌는 곳마다 세로선
    let days = "";
    for (let d = new Date(t0); d.getTime() <= t1; d = new Date(d.getTime() + 86400000)) { const m = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1).getTime(); if (m < t1) days += `<line x1="${X(m)}" x2="${X(m)}" y1="${TOP}" y2="${H - B}" stroke="var(--line)" stroke-width="1"/><text x="${X(m) + 3}" y="${TOP + 10}">${new Date(m).getMonth() + 1}/${new Date(m).getDate()}</text>`; }
    const dots = pts.map((p) => `<circle cx="${X(p.t)}" cy="${Y(p.y)}" r="${pts.length > 40 ? 0 : 3}" fill="${color}" stroke="var(--surface)" stroke-width="1.5"/><rect x="${X(p.t) - 6}" y="${TOP}" width="12" height="${H - TOP - B}" fill="transparent" data-tip="${p.at.slice(5)} · ${n(p.y)}회"/>`).join("");
    return `<div class="mini"><div class="mt"><span class="rk">${rank + 1}</span>${v.title}</div><div class="mv">${n(last.y)}<span class="plus">${gain > 0 ? "+" + n(gain) : ""}</span></div>
      <svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="${v.title} 조회수 변화">
        <line x1="${L}" x2="${W - R}" y1="${H - B}" y2="${H - B}" stroke="var(--line)"/>${days}
        <polyline fill="none" stroke="${color}" stroke-width="2" stroke-linejoin="round" points="${pts.map((p) => X(p.t) + "," + Y(p.y)).join(" ")}"/>${dots}
        <text x="${L}" y="${H - 6}">${hh(t0)}</text><text x="${W - R}" y="${H - 6}" text-anchor="end">${hh(t1)}</text>
      </svg></div>`;
  }).join("");
};
minis("line", tot, "var(--ink)");                         // 세 곳 합계
minis("line_tt", (v) => v.tiktok || 0, "var(--tiktok)");  // 틱톡만
const tip = document.getElementById("tip");
if (window.__tipBound) return;
window.__tipBound = true;
document.addEventListener("mousemove", (e) => {
  const s = e.target.closest("[data-tip]");
  if (!s) { tip.style.display = "none"; return; }
  tip.textContent = s.dataset.tip; tip.style.display = "block";
  tip.style.left = Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 8) + "px"; tip.style.top = e.clientY - 34 + "px";
});
}
let LAST = EMBED;
render(EMBED);
let __rz; window.addEventListener("resize", () => { clearTimeout(__rz); __rz = setTimeout(() => render(LAST), 200); });
// 깃허브에 올라간 최신 기록을 직접 가져와 다시 그린다(3분마다). 실패하면 화면에 들어 있는 값을 그대로 둔다.
// raw 주소를 먼저 쓴다. api.github.com은 로그인 없이 한 시간에 60번까지만 되어, 여러 기기에서 열어 두면 막힌다.
async function live() {
  const tries = [
    ["https://raw.githubusercontent.com/Lee-SeungYeol/whyshape-views/main/data.json?t=" + Date.now(), {}],
    ["https://api.github.com/repos/Lee-SeungYeol/whyshape-views/contents/data.json", { headers: { Accept: "application/vnd.github.raw+json" } }],
  ];
  for (const [url, opt] of tries) {
    try {
      const r = await fetch(url, { ...opt, cache: "no-store" });
      if (!r.ok) continue;
      const d = await r.json();
      if (d.snapshots && d.snapshots.length >= LAST.snapshots.length) { LAST = d; render(LAST); }
      return;
    } catch (e) {}
  }
}
live();
setInterval(live, 60000);
</script>
</body>
</html>
"""

out = os.path.join(HERE, "index.html")
open(out, "w", encoding="utf-8").write(HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False)))
print("written", out)
