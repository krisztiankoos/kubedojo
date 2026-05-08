from __future__ import annotations


AFK_NOTIFY_CSS = """
    .afk-notify{position:fixed;right:18px;bottom:18px;z-index:30;display:flex;align-items:center;gap:10px;max-width:min(440px,calc(100vw - 36px));border:1px solid rgba(61,214,198,.5);background:#121416;color:var(--text);border-radius:6px;padding:10px 12px;box-shadow:0 18px 60px rgba(0,0,0,.4);font-size:13px}
    .afk-notify[hidden]{display:none}
    .afk-notify span{color:var(--text);font-size:13px;margin:0}
    .afk-notify button{border:1px solid var(--line);border-radius:5px;background:var(--panel-2);color:var(--text);padding:6px 9px;font-size:12px;font-weight:800;cursor:pointer;white-space:nowrap}
    .afk-notify button:first-of-type{background:var(--teal);border-color:var(--teal);color:#071211}
"""


def render_afk_notify_markup() -> str:
    return """
<div class="afk-notify" id="afk-notify" hidden>
  <span>Get notified when decisions need your call</span>
  <button type="button" id="afk-notify-enable">Enable</button>
  <button type="button" id="afk-notify-dismiss">Not now</button>
</div>
<script>
(() => {
  const OPT_OUT = "kdjo_notify_optout";
  const SNAPSHOT = "kdjo_pending_files";
  const POLL_MS = 60000;
  const banner = document.getElementById("afk-notify");
  const enable = document.getElementById("afk-notify-enable");
  const dismiss = document.getElementById("afk-notify-dismiss");
  const supported = "Notification" in window;
  const optedOut = () => localStorage.getItem(OPT_OUT) === "1";
  function readSnapshot() {
    try {
      const parsed = JSON.parse(localStorage.getItem(SNAPSHOT) || "[]");
      if (Array.isArray(parsed)) {
        return new Map(parsed.map(item => {
          if (typeof item === "string") return [item, {is_stale: false}];
          return [String(item.filename || ""), {is_stale: !!item.is_stale}];
        }).filter(([name]) => name));
      }
      return new Map(Object.entries(parsed || {}).map(([name, state]) => [
        String(name),
        {is_stale: !!(state && state.is_stale)}
      ]));
    } catch {
      return new Map();
    }
  }
  function writeSnapshot(files) {
    const snapshot = files
      .filter(file => file && file.filename)
      .map(file => ({filename: String(file.filename), is_stale: !!file.is_stale}));
    localStorage.setItem(SNAPSHOT, JSON.stringify(snapshot));
  }
  function ageLabel(file) {
    if (file.is_stale) return "stale (>24h)";
    const age = Math.max(0, Math.floor((Date.now() - Number(file.mtime || 0) * 1000) / 1000));
    if (age < 60) return age + "s ago";
    if (age < 3600) return Math.floor(age / 60) + "m ago";
    if (age < 86400) return Math.floor(age / 3600) + "h ago";
    return Math.floor(age / 86400) + "d ago";
  }
  function suppressNotifications() {
    return document.visibilityState === "visible" && window.location.pathname === "/decisions";
  }
  function notify(title, file) {
    if (!supported || optedOut() || Notification.permission !== "granted" || suppressNotifications()) return;
    const notification = new Notification(title, {
      body: file.filename + " — " + ageLabel(file),
      tag: "kdjo-decision-" + file.filename
    });
    notification.onclick = () => {
      window.focus();
      window.location.href = "/decisions#card-" + encodeURIComponent(file.filename);
      notification.close();
    };
  }
  async function pollPendingDecisions() {
    if (optedOut()) return;
    try {
      const res = await fetch("/api/decisions/pending", {cache: "no-store"});
      if (!res.ok) return;
      const data = await res.json();
      const files = Array.isArray(data.files) ? data.files : [];
      const previous = readSnapshot();
      files.forEach(file => {
        if (!file || !file.filename) return;
        const before = previous.get(String(file.filename));
        if (!before) notify("Decision pending", file);
        else if (!before.is_stale && file.is_stale) notify("Decision stale", file);
      });
      writeSnapshot(files);
    } catch {
      // Local monitor pages should stay quiet when the API is unavailable.
    }
  }
  function maybeShowBanner() {
    if (!banner || !supported || optedOut() || Notification.permission !== "default") return;
    banner.hidden = false;
  }
  enable?.addEventListener("click", async () => {
    if (!supported || optedOut()) return;
    banner.hidden = true;
    await Notification.requestPermission();
    await pollPendingDecisions();
  });
  dismiss?.addEventListener("click", () => {
    localStorage.setItem(OPT_OUT, "1");
    if (banner) banner.hidden = true;
  });
  maybeShowBanner();
  pollPendingDecisions();
  setInterval(pollPendingDecisions, POLL_MS);
})();
</script>"""
