/* Kiosk Home: renders the dashboard cards and opens the tapped one. */
"use strict";

const $ = (id) => document.getElementById(id);

function esc(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
}

function render(data) {
    $("cards").innerHTML = data.dashboards.map((d) => {
        const status = d.online
            ? `<span class="dot online"></span>ONLINE`
            : `<span class="dot offline"></span><span class="offline-text">OFFLINE</span>`;
        return `<a class="card" href="${location.protocol}//${location.hostname}:${d.port}/">` +
            `<span class="icon">${d.icon}</span>` +
            `<span class="name">${esc(d.name)}</span>` +
            `<span class="tagline">${esc(d.tagline)}</span>` +
            `<span class="fact">${esc(d.fact || "")}</span>` +
            `<span class="status">${status}</span>` +
            `</a>`;
    }).join("");
}

async function load() {
    try {
        const r = await fetch("/api/dashboards");
        render(await r.json());
    } catch (e) {
        $("cards").innerHTML =
            `<div class="card"><span class="name">Kiosk Home</span>` +
            `<span class="tagline">could not read dashboard list</span></div>`;
    }
}

function tick() {
    const d = new Date();
    $("clock").textContent =
        `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

load();
tick();
setInterval(load, 60000);
setInterval(tick, 1000);
