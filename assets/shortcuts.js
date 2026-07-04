// Left/Right arrow keys cycle through the dashboard tabs
// (ignored while typing in an input or dropdown).
document.addEventListener("keydown", function (e) {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    var tag = (e.target.tagName || "").toUpperCase();
    if (tag === "INPUT" || tag === "TEXTAREA" || e.target.isContentEditable) return;

    var tabs = Array.prototype.slice.call(document.querySelectorAll("#main-tabs .tab"));
    if (!tabs.length) return;
    var idx = tabs.findIndex(function (t) { return t.classList.contains("tab--selected"); });
    if (idx === -1) return;
    var next = e.key === "ArrowRight" ? idx + 1 : idx - 1;
    next = (next + tabs.length) % tabs.length;
    tabs[next].click();
});
