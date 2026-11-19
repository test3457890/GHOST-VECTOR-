// GHOST VECTOR recovery terminal. Loaded as a file so the CSP can forbid inline script.
"use strict";

async function post(url, body) {
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "same-origin",
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) return { ok: false, message: data.message || "ACCESS DENIED (" + r.status + ")" };
    return data;
  } catch (e) {
    return { ok: false, message: "LINK DOWN. Check your connection." };
  }
}

function show(el, res) {
  el.className = "msg " + (res.ok ? "ok" : "bad");
  el.textContent = "> " + res.message;
}

function busy(el, text) {
  el.className = "msg warn";
  el.textContent = "> " + text;
}

function on(id, fn) {
  const el = document.getElementById(id);
  if (el) el.addEventListener("click", fn);
}

function onEnter(id, fn) {
  const el = document.getElementById(id);
  if (el) el.addEventListener("keydown", (e) => { if (e.key === "Enter") fn(); });
}

async function uplink() {
  const m = document.getElementById("m");
  busy(m, "transmitting...");
  const res = await post("/api/uplink", { flag: document.getElementById("flag").value });
  show(m, res);
  if (res.ok && res.next) setTimeout(() => { window.location.href = res.next; }, 1500);
}

async function lockMarkers() {
  const codes = [0, 1, 2, 3].map((i) => document.getElementById("c" + i).value);
  const m = document.getElementById("m1");
  busy(m, "aligning...");
  const res = await post("/api/handshake", { codes });
  let s = res.message;
  if (res.results) s += "  [" + res.results.map((r, i) => "V" + (i + 1) + (r ? ":OK" : ":X")).join(" ") + "]";
  show(m, { ok: res.ok, message: s });
}

async function transmit() {
  const m = document.getElementById("m2");
  busy(m, "transmitting...");
  const res = await post("/api/transmit", { coordinate: document.getElementById("coord").value });
  show(m, res);
  const box = document.getElementById("flagbox");
  if (res.ok && res.flag && box) {
    box.hidden = false;
    document.getElementById("finalflag").textContent = res.flag;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  on("send-uplink", uplink);
  onEnter("flag", uplink);
  on("lock", lockMarkers);
  on("tx", transmit);
  onEnter("coord", transmit);
});
