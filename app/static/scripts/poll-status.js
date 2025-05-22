// app/static/scripts/poll-status.js
document.addEventListener("DOMContentLoaded", function () {
  const taskId = window.TASK_ID; // We'll pass this via a script tag
  function pollStatus() {
    if (!taskId) return;
    const statusEl = document.getElementById("crawl-status");
    const progressEl = document.getElementById("progress-bar");
    fetch(`/status/${taskId}`)
      .then((r) => r.json())
      .then((data) => {
        statusEl.textContent = data.status || "Waiting...";
        if (
          data.progress &&
          data.progress.percent !== undefined &&
          progressEl
        ) {
          progressEl.style.width = data.progress.percent + "%";
        }
        if (!data.finished) {
          setTimeout(pollStatus, 2000);
        } else {
          if (progressEl) progressEl.style.width = "100%";
          statusEl.textContent = (data.status || "") + " (Done)";
          setTimeout(() => window.location.reload(), 1200);
        }
      });
  }
  if (taskId && document.getElementById("crawl-status")) {
    pollStatus();
  }
});
