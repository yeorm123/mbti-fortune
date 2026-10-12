// 오늘의 MBTI 운세 — 날짜 + 유형으로 문구를 골라 매일 다른 조합을 보여준다.

const TYPES = [
  "ISTJ", "ISFJ", "INFJ", "INTJ",
  "ISTP", "ISFP", "INFP", "INTP",
  "ESTP", "ESFP", "ENFP", "ENTP",
  "ESTJ", "ESFJ", "ENFJ", "ENTJ",
];
const WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"];
const STORE_KEY = "mbti-fortune:type";

const $ = (id) => document.getElementById(id);
let data = null;
let current = { type: null, date: new Date() };

// 같은 날짜·유형이면 언제 열어도 같은 결과가 나오도록 하는 간단한 해시
function seed(str) {
  let h = 2166136261;
  for (const ch of str) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return h >>> 0;
}
const pick = (list, key) => list[seed(key) % list.length];

function dateKey(d) {
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${m}-${day}`;
}

function render() {
  const { type, date } = current;
  const t = data.types[type];
  const key = `${dateKey(date)}:${type}`;

  $("date").textContent = `${date.getMonth() + 1}월 ${date.getDate()}일 (${WEEKDAYS[date.getDay()]})`;
  $("type").textContent = type;
  $("nickname").textContent = t.nickname;
  $("one-line").textContent = pick(t.one_line, key + ":one");
  $("relationship").textContent = pick(t.relationship, key + ":rel");
  $("work").textContent = pick(t.work_study, key + ":work");
  $("rhythm").textContent = pick(t.daily_rhythm, key + ":rhythm");
  $("lucky-color").textContent = pick(data.lucky.colors, key + ":color");
  $("lucky-item").textContent = pick(data.lucky.items, key + ":item");

  $("pick").hidden = true;
  $("result").hidden = false;
  history.replaceState(null, "", `#${type}`);
}

function choose(type) {
  current.type = type;
  current.date = new Date();
  try { localStorage.setItem(STORE_KEY, type); } catch {}
  render();
}

function shiftDay(n) {
  current.date = new Date(current.date.getFullYear(), current.date.getMonth(), current.date.getDate() + n);
  render();
}

function showPicker() {
  $("result").hidden = true;
  $("pick").hidden = false;
  history.replaceState(null, "", location.pathname);
}

async function share() {
  const url = `${location.origin}${location.pathname}#${current.type}`;
  try {
    await navigator.clipboard.writeText(url);
    $("toast").textContent = "링크를 복사했어요!";
  } catch {
    $("toast").textContent = url;
  }
  setTimeout(() => ($("toast").textContent = ""), 2500);
}

async function init() {
  data = await (await fetch("fortunes.json")).json();

  $("grid").append(...TYPES.map((type) => {
    const b = document.createElement("button");
    b.textContent = type;
    b.addEventListener("click", () => choose(type));
    return b;
  }));
  $("prev").addEventListener("click", () => shiftDay(-1));
  $("next").addEventListener("click", () => shiftDay(1));
  $("change").addEventListener("click", showPicker);
  $("share").addEventListener("click", share);

  // 링크(#ENFP) > 지난번 선택 순으로 바로 결과 보여주기
  let saved = null;
  try { saved = localStorage.getItem(STORE_KEY); } catch {}
  const fromHash = location.hash.slice(1).toUpperCase();
  const start = TYPES.includes(fromHash) ? fromHash : TYPES.includes(saved) ? saved : null;
  if (start) choose(start);
}

init();
