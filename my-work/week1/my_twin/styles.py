"""Styling constants for the digital twin Gradio app.

Token system:
  GOLD   -> amber "highlight" accent (primary CTA, user bubble)
  BLUE   -> teal "signal" accent (focus states, links, interactive)
  PURPLE -> slate-indigo "structure" accent (assistant stripe, dividers)
"""

STEELBLUE = "#3d7cc9"
CYAN = "#5ec8d8"
SLATE = "#56637f"

EXAMPLES = [
    "Tell me about your background and experience.",
    "What kinds of projects are you working on now?",
    "What are your strongest technical skills?",
    "How can I get in touch with you?",
]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  --twin-signal: #5ec8d8;
  --twin-highlight: #3d7cc9;
  --twin-structure: #56637f;
  --twin-on-highlight: #f4f8fc;

  --twin-bg: #0a0e14;
  --twin-surface: #121822;
  --twin-surface-2: #182030;
  --twin-border: #26303f;
  --twin-border-strong: #384356;
  --twin-text: #e8edf4;
  --twin-muted: #7c8ba0;

  --twin-font-display: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
  --twin-font-body: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --twin-font-mono: 'IBM Plex Mono', 'SF Mono', Menlo, monospace;

  --twin-radius-sm: 3px;
  --twin-radius-md: 8px;
}

/* Light mode: Gradio adds `.dark` to <body> when dark; absence = light.
   Only the neutral palette flips — signal/highlight/structure accents stay identical. */
body:not(.dark) {
  --twin-bg: #f3f6fa;
  --twin-surface: #ffffff;
  --twin-surface-2: #e9eef4;
  --twin-border: #d7dfe8;
  --twin-border-strong: #b9c5d3;
  --twin-text: #101822;
  --twin-muted: #5c6b80;
}

footer, .built-with, .show-api, .api-docs { display: none !important; }

html, body, gradio-app {
  background-color: var(--twin-bg) !important;
  background-image: radial-gradient(var(--twin-border) 1px, transparent 1px) !important;
  background-size: 22px 22px !important;
}

/* ---------- Stable layout ---------- */
.gradio-container {
  background: transparent !important;
  color: var(--twin-text) !important;
  font-family: var(--twin-font-body) !important;
  width: 100% !important;
  max-width: 880px !important;
  min-width: 0 !important;
  margin: 0 auto !important;
  padding: 40px 24px 48px !important;
}
.gradio-container .main, .gradio-container .contain, .gradio-container .wrap {
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
}
.gradio-container * { min-width: 0; }

/* ---------- Title + signature signal-line divider ---------- */
.gradio-container h1 {
  color: var(--twin-text) !important;
  font-family: var(--twin-font-display) !important;
  font-size: 27px !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em !important;
  margin: 4px 0 0 !important;
  text-align: left !important;
}
.gradio-container h1::after {
  content: "";
  display: block;
  width: 216px;
  height: 26px;
  margin: 10px 0 22px;
  background-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%20200%2040'%3E%3Cpath%20d='M0,30%20L20,10%20L40,25%20L60,5%20L80,20%20L100,8%20L120,28%20L140,12%20L160,22%20L180,6%20L200,18'%20fill='none'%20stroke='%235ec8d8'%20stroke-width='2.5'%20stroke-linecap='round'%20stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: left center;
  background-size: contain;
}
.gradio-container h1 + * p,
.gradio-container h1 ~ .prose p:first-of-type {
  color: var(--twin-muted) !important;
  font-family: var(--twin-font-mono) !important;
  font-size: 12px !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
}

/* ---------- Soft technical corners on structural pieces ---------- */
.chatbot, .block, .form, .examples button {
  border-radius: var(--twin-radius-md) !important;
}
button, input, textarea {
  border-radius: var(--twin-radius-sm) !important;
}

/* ---------- Block surfaces ---------- */
.block, .form { background: transparent !important; box-shadow: none !important; }

/* ---------- Hide the Chatbot label / header strip ---------- */
.chatbot > .block-label,
.chatbot > label,
.chatbot .label-wrap,
.chatbot .block-label,
.chatbot > .label-container {
  display: none !important;
}

/* ---------- Chatbot frame ---------- */
.chatbot, .chatbot.block {
  background: var(--twin-surface) !important;
  border: 1px solid var(--twin-border) !important;
  min-height: 460px !important;
  box-shadow: none !important;
}
.chatbot .placeholder, .chatbot .placeholder * { color: var(--twin-muted) !important; }

/* ---------- Message rows: strip parent backgrounds ---------- */
.message-row,
.message-row > div,
.message-row .role,
.message-wrap, .bubble-wrap {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

/* ---------- Reset borders on every bubble variant first ---------- */
.message-row .message,
.message-row .message-bubble,
.message-row .bubble {
  border: 0 !important;
  box-shadow: none !important;
  padding: 8px 12px !important;
  border-radius: var(--twin-radius-sm) !important;
}

/* ---------- Bubble backgrounds (broad to cover Gradio variants) ---------- */
.message-row.user-row .message,
.message-row.user-row .message-bubble,
.message-row.user-row .bubble,
.message-row[data-role="user"] .message,
.message-row[data-role="user"] .message-bubble {
  background: var(--twin-highlight) !important;
  color: var(--twin-on-highlight) !important;
}

.message-row.bot-row .message,
.message-row.bot-row .message-bubble,
.message-row.bot-row .bubble,
.message-row[data-role="assistant"] .message,
.message-row[data-role="assistant"] .message-bubble {
  background: var(--twin-surface-2) !important;
  color: var(--twin-text) !important;
}

/* ---------- Structure stripe ----------
   Apply to every common bubble class for assistant rows (we don't know which
   one the running Gradio uses), then suppress on any *nested* instance so the
   stripe lands on the outermost matching element only — exactly one stripe. */
.message-row.bot-row .message,
.message-row.bot-row .bubble,
.message-row.bot-row .message-bubble,
.message-row[data-role="assistant"] .message,
.message-row[data-role="assistant"] .bubble,
.message-row[data-role="assistant"] .message-bubble {
  border-left: 2px solid var(--twin-structure) !important;
}

.message-row.bot-row .message .message,
.message-row.bot-row .message .bubble,
.message-row.bot-row .message .message-bubble,
.message-row.bot-row .bubble .message,
.message-row.bot-row .bubble .bubble,
.message-row.bot-row .bubble .message-bubble,
.message-row.bot-row .message-bubble .message,
.message-row.bot-row .message-bubble .bubble,
.message-row.bot-row .message-bubble .message-bubble,
.message-row[data-role="assistant"] .message .message,
.message-row[data-role="assistant"] .message .bubble,
.message-row[data-role="assistant"] .message .message-bubble,
.message-row[data-role="assistant"] .bubble .message,
.message-row[data-role="assistant"] .bubble .bubble,
.message-row[data-role="assistant"] .bubble .message-bubble,
.message-row[data-role="assistant"] .message-bubble .message,
.message-row[data-role="assistant"] .message-bubble .bubble,
.message-row[data-role="assistant"] .message-bubble .message-bubble {
  border-left: 0 !important;
}

/* ---------- Uniform font size in bubbles ----------
   The "first paragraph different size" was caused by a leaky `.prose p:first-of-type`
   selector. Force every paragraph in a bubble to the same size. */
.message-row .message,
.message-row .message-bubble,
.message-row .bubble {
  font-size: 14.5px !important;
  line-height: 1.6 !important;
}
.message-row .message p,
.message-row .message-bubble p,
.message-row .bubble p,
.message-row .prose p {
  font-size: 14.5px !important;
  line-height: 1.6 !important;
  margin: 0 0 8px !important;
  color: inherit !important;
}
.message-row .message p:last-child,
.message-row .message-bubble p:last-child,
.message-row .bubble p:last-child,
.message-row .prose p:last-child { margin-bottom: 0 !important; }

/* Strip stray internal borders/backgrounds from anything inside a bubble */
.message-row .message *,
.message-row .message-bubble *,
.message-row .bubble * {
  background: transparent !important;
  border-color: transparent !important;
  box-shadow: none !important;
  color: inherit !important;
}
.message-row .message a,
.message-row .message-bubble a {
  color: var(--twin-signal) !important;
  text-decoration: underline;
}
.message-row.user-row .message a,
.message-row.user-row .message-bubble a {
  color: var(--twin-on-highlight) !important;
  text-decoration-color: rgba(244, 248, 252, 0.6) !important;
}

/* ---------- Code blocks: mono face, quiet surface ---------- */
.message-row code, .message-row pre {
  font-family: var(--twin-font-mono) !important;
  font-size: 13px !important;
}
.message-row pre {
  background: rgba(0, 0, 0, 0.18) !important;
  border: 1px solid var(--twin-border) !important;
  border-radius: var(--twin-radius-sm) !important;
}

/* ---------- Input row alignment ---------- */
.input-row,
.gr-input-row,
.chat-input-row,
form[class*="input"] { align-items: stretch !important; }

textarea, input[type="text"] {
  background: var(--twin-surface) !important;
  border: 1px solid var(--twin-border) !important;
  color: var(--twin-text) !important;
  font-family: var(--twin-font-body) !important;
  font-size: 14.5px !important;
  padding: 12px 14px !important;
  line-height: 1.4 !important;
  min-height: 48px !important;
}
textarea:focus, input[type="text"]:focus {
  border-color: var(--twin-signal) !important;
  outline: none !important;
  box-shadow: 0 0 0 1px var(--twin-signal) !important;
}
textarea::placeholder, input::placeholder { color: var(--twin-muted) !important; }

/* ---------- Buttons ---------- */
button {
  font-family: var(--twin-font-mono) !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  border: 1px solid var(--twin-border) !important;
  background: transparent !important;
  color: var(--twin-text) !important;
  padding: 0 16px !important;
  min-height: 48px !important;
  align-self: stretch !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer;
  transition: background 0.12s ease, color 0.12s ease, border-color 0.12s ease;
}
button:hover { border-color: var(--twin-signal) !important; color: var(--twin-signal) !important; }

button.primary,
button[variant="primary"],
button.submit,
button.submit-button,
.submit-button,
button.lg.primary {
  background: var(--twin-highlight) !important;
  border: 1px solid var(--twin-highlight) !important;
  color: var(--twin-on-highlight) !important;
  min-height: 48px !important;
  align-self: stretch !important;
  padding: 0 14px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
button.primary:hover,
button.submit:hover,
.submit-button:hover,
button.lg.primary:hover {
  background: #4f8ed6 !important;
  border-color: #4f8ed6 !important;
  color: var(--twin-on-highlight) !important;
}

/* ---------- Submit-button icon: center vertically and size correctly ---------- */
button.submit svg,
button.submit-button svg,
.submit-button svg,
button.primary svg,
button[variant="primary"] svg {
  width: 18px !important;
  height: 18px !important;
  margin: 0 auto !important;
  display: block !important;
  align-self: center !important;
  color: var(--twin-on-highlight) !important;
  fill: currentColor !important;
  stroke: currentColor !important;
}

/* ---------- Examples ---------- */
.examples, .examples-holder, [data-testid="examples"] {
  background: transparent !important;
  padding: 0 !important;
  margin-top: 16px !important;
}
.examples table, .examples-table { background: transparent !important; border: 0 !important; }
.examples button, .example, .examples td button, [data-testid="examples"] button {
  background: var(--twin-surface) !important;
  border: 1px solid var(--twin-border) !important;
  color: var(--twin-text) !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  font-family: var(--twin-font-body) !important;
  font-size: 13.5px !important;
  font-weight: 400 !important;
  padding: 10px 14px !important;
  text-align: left !important;
  min-height: 0 !important;
  align-self: auto !important;
  display: inline-block !important;
}
.examples button:hover, .example:hover, [data-testid="examples"] button:hover {
  border-color: var(--twin-signal) !important;
  color: var(--twin-signal) !important;
  background: var(--twin-surface) !important;
}

/* ---------- Icon buttons (clear, retry, copy) ---------- */
.icon-button, .chatbot .icon-button {
  color: var(--twin-muted) !important;
  background: transparent !important;
  border: 0 !important;
  min-height: 0 !important;
  align-self: auto !important;
  padding: 4px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
.icon-button:hover, .chatbot .icon-button:hover { color: var(--twin-highlight) !important; }

/* ---------- Focus visibility (accessibility floor) ---------- */
button:focus-visible,
.examples button:focus-visible,
.icon-button:focus-visible {
  outline: 2px solid var(--twin-signal) !important;
  outline-offset: 2px !important;
}

/* ---------- Scrollbar ---------- */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--twin-bg); }
::-webkit-scrollbar-thumb { background: var(--twin-border-strong); }
::-webkit-scrollbar-thumb:hover { background: var(--twin-signal); }

/* ---------- Selection ---------- */
::selection { background: var(--twin-highlight); color: var(--twin-on-highlight); }

/* ---------- Reduced motion ---------- */
@media (prefers-reduced-motion: reduce) {
  button, .examples button, .icon-button { transition: none !important; }
}

/* ---------- Mobile ---------- */
@media (max-width: 640px) {
  .gradio-container { padding: 28px 14px 36px !important; }
  .gradio-container h1 { font-size: 22px !important; }
  .gradio-container h1::after { width: 168px !important; }
}
"""

JS = """
() => {
  document.title = "Michael's Digital Twin";

  const focusInput = () => {
    const areas = document.querySelectorAll('textarea');
    if (areas.length) areas[areas.length - 1].focus();
  };
  setTimeout(focusInput, 300);

  // Re-focus the message field whenever Gradio re-enables it
  // (i.e. after the assistant finishes responding).
  const watchTextarea = (area) => {
    if (area.dataset.twinWatched) return;
    area.dataset.twinWatched = '1';
    let wasDisabled = area.disabled || area.readOnly;
    new MutationObserver(() => {
      const isDisabled = area.disabled || area.readOnly;
      if (wasDisabled && !isDisabled) area.focus();
      wasDisabled = isDisabled;
    }).observe(area, { attributes: true, attributeFilter: ['disabled', 'readonly'] });
  };

  const scan = () => document.querySelectorAll('textarea').forEach(watchTextarea);
  setTimeout(scan, 500);
  new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
}
"""