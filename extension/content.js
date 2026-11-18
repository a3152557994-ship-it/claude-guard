(() => {
  if (window.__CLAUDE_GUARD_CONTENT_LOADED__) return;
  window.__CLAUDE_GUARD_CONTENT_LOADED__ = true;

  function extractConversationFromDom() {
    const title =
      document.querySelector('[data-testid="chat-title-button"]')?.textContent?.trim() ||
      document.title.replace(/\s*[-|]\s*Claude.*$/i, "").trim() ||
      "Claude Session";

    const messages = [];
    // Support both claude.ai DOM selectors and generic chat/article fallback
    const userNodes = document.querySelectorAll(
      '[data-testid="user-message"], .font-user-message, [data-message-author-role="user"]'
    );
    const assistantNodes = document.querySelectorAll(
      '.font-claude-message, [data-testid="assistant-message"], [data-message-author-role="assistant"]'
    );

    if (userNodes.length > 0 || assistantNodes.length > 0) {
      const allTurnNodes = document.querySelectorAll(
        '[data-testid="user-message"], .font-user-message, [data-message-author-role="user"], .font-claude-message, [data-testid="assistant-message"], [data-message-author-role="assistant"]'
      );
      allTurnNodes.forEach((el) => {
        const isUser =
          el.matches('[data-testid="user-message"], .font-user-message, [data-message-author-role="user"]');
        const text = (el.innerText || el.textContent || "").trim();
        if (text) {
          messages.push({
            role: isUser ? "user" : "assistant",
            text,
          });
        }
      });
    } else {
      // Fallback: extract main paragraphs/sections if testing on another page
      const mainEl = document.querySelector("main, article") || document.body;
      const sampleText = (mainEl.innerText || "").trim().slice(0, 4000);
      if (sampleText) {
        messages.push({
          role: "assistant",
          text: sampleText,
        });
      }
    }

    const artifacts = [];
    document.querySelectorAll("pre code").forEach((codeEl, idx) => {
      const code = (codeEl.innerText || codeEl.textContent || "").trim();
      if (code.length > 12) {
        const cls = codeEl.className || "";
        const langMatch = cls.match(/language-([a-z0-9_+-]+)/i);
        artifacts.push({
          title: `Code Block #${idx + 1}`,
          language: langMatch ? langMatch[1] : "text",
          code,
        });
      }
    });

    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
    const utcOffsetMinutes = -new Date().getTimezoneOffset();

    return {
      id: location.pathname && location.pathname.length > 1 ? location.pathname : "/session-current",
      title,
      url: location.href,
      capturedAt: new Date().toISOString(),
      messages,
      artifacts,
      env: {
        timezone: tz,
        utcOffsetMinutes,
        languages: navigator.languages ? Array.from(navigator.languages) : [navigator.language || "en-US"],
      },
    };
  }

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg?.type === "CAPTURE_CURRENT_CHAT") {
      try {
        const data = extractConversationFromDom();
        sendResponse({ ok: true, data });
      } catch (err) {
        sendResponse({ ok: false, error: err.message });
      }
      return true;
    }
    return false;
  });
})();
