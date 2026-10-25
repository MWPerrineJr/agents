EXAMPLES = [
    "Most popular AI Agent frameworks in 2026",
    "Most commercially successful Agentic AI implementations in 2026",
    "How are enterprises adopting multi-agent systems in 2026?",
]

HEADER_HTML = """
<div class="dr-hero">
    <div class="dr-orb dr-orb-a" aria-hidden="true"></div>
    <div class="dr-orb dr-orb-b" aria-hidden="true"></div>
    <div class="dr-brand">
        <div class="dr-mark" aria-hidden="true">
            <span class="dr-ring"></span>
            <span class="dr-core"></span>
        </div>
        <div class="dr-titles">
            <p class="dr-kicker">OpenAI Agents · Web search</p>
            <h1>Deep<span class="dr-sep">Research</span></h1>
            <p class="dr-tagline">Plan searches. Investigate in parallel. Deliver a report.</p>
        </div>
    </div>
</div>
"""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Fraunces:opsz,wght@9..144,600;9..144,700&family=JetBrains+Mono:wght@400;500&display=swap');

.gradio-container {
    --dr-ink: #14212b;
    --dr-muted: #5c6b76;
    --dr-line: #d5dde3;
    --dr-surface: rgba(255, 252, 248, 0.82);
    --dr-surface-solid: #fffdf9;
    --dr-teal: #0f766e;
    --dr-teal-deep: #0b5f59;
    --dr-sand: #e8dcc8;
    --dr-sky: #7eb8c9;
    --dr-focus: #1a8f86;

    max-width: 920px !important;
    margin: 0 auto !important;
    padding: 2.75rem 1.5rem 4.5rem !important;
    color: var(--dr-ink) !important;
    font-family: "DM Sans", sans-serif !important;
    background:
        radial-gradient(1200px 600px at 8% -10%, rgba(126, 184, 201, 0.35), transparent 55%),
        radial-gradient(900px 500px at 100% 0%, rgba(232, 220, 200, 0.55), transparent 50%),
        linear-gradient(180deg, #f3f0ea 0%, #e9eef1 48%, #e7ece8 100%) !important;
    position: relative !important;
}

.gradio-container::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.35;
    background-image:
        linear-gradient(rgba(20, 33, 43, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(20, 33, 43, 0.03) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: linear-gradient(180deg, #000 0%, transparent 85%);
    z-index: 0;
}

.gradio-container > * { position: relative; z-index: 1; }

body {
    background: #e9eef1 !important;
}

/* === HERO / BRAND === */
.dr-hero {
    position: relative;
    margin-bottom: 2.25rem;
    padding: 0.25rem 0 1.75rem;
    overflow: hidden;
}

.dr-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(28px);
    opacity: 0.45;
    pointer-events: none;
    animation: dr-drift 12s ease-in-out infinite;
}

.dr-orb-a {
    width: 180px;
    height: 180px;
    background: var(--dr-sky);
    top: -60px;
    right: 8%;
}

.dr-orb-b {
    width: 140px;
    height: 140px;
    background: var(--dr-sand);
    top: 10px;
    right: 22%;
    animation-delay: -4s;
}

@keyframes dr-drift {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-12px, 8px) scale(1.06); }
}

.dr-brand {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 1.15rem;
    align-items: center;
}

.dr-mark {
    width: 52px;
    height: 52px;
    position: relative;
    display: grid;
    place-items: center;
}

.dr-ring {
    position: absolute;
    inset: 0;
    border: 2px solid var(--dr-ink);
    border-radius: 14px;
    transform: rotate(12deg);
    animation: dr-ring-in 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.dr-core {
    width: 18px;
    height: 18px;
    background: var(--dr-teal);
    border-radius: 5px;
    transform: rotate(-8deg);
    box-shadow: 8px -6px 0 0 var(--dr-sand);
    animation: dr-core-in 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.08s both;
}

@keyframes dr-ring-in {
    from { opacity: 0; transform: rotate(12deg) scale(0.7); }
    to { opacity: 1; transform: rotate(12deg) scale(1); }
}

@keyframes dr-core-in {
    from { opacity: 0; transform: rotate(-8deg) translateY(6px); }
    to { opacity: 1; transform: rotate(-8deg) translateY(0); }
}

.dr-kicker {
    margin: 0 0 0.35rem;
    font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--dr-muted);
}

.dr-titles h1 {
    margin: 0;
    font-family: "Fraunces", Georgia, serif;
    font-size: clamp(2.15rem, 5vw, 3.1rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.05;
    color: var(--dr-ink);
}

.dr-sep {
    color: var(--dr-teal);
    margin-left: 0.18em;
}

.dr-tagline {
    margin: 0.55rem 0 0;
    font-size: 1.02rem;
    color: var(--dr-muted);
    max-width: 34ch;
    line-height: 1.45;
}

/* === QUERY ROW === */
.dr-query-row {
    gap: 0.75rem !important;
    align-items: stretch !important;
    background: var(--dr-surface) !important;
    border: 1px solid rgba(20, 33, 43, 0.1) !important;
    border-radius: 18px !important;
    padding: 0.55rem !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 18px 40px -28px rgba(20, 33, 43, 0.45) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

.dr-query-row:focus-within {
    border-color: rgba(15, 118, 110, 0.45) !important;
    box-shadow:
        0 18px 40px -28px rgba(20, 33, 43, 0.45),
        0 0 0 3px rgba(26, 143, 134, 0.18) !important;
}

#dr-query, #dr-query > div, #dr-query .wrap, #dr-query .form, #dr-query .block {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    border-radius: 0 !important;
}

#dr-query textarea, #dr-query input {
    background: transparent !important;
    color: var(--dr-ink) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 1rem !important;
    font-size: 1.05rem !important;
    font-family: "DM Sans", sans-serif !important;
    box-shadow: none !important;
    line-height: 1.45 !important;
    resize: none !important;
    min-height: 52px !important;
}

#dr-query textarea:focus, #dr-query input:focus {
    outline: none !important;
    box-shadow: none !important;
}

#dr-query textarea::placeholder, #dr-query input::placeholder {
    color: #8a98a3 !important;
    opacity: 1 !important;
}

#dr-run {
    background: var(--dr-teal) !important;
    color: #f7fffe !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: "DM Sans", sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    font-size: 0.95rem !important;
    box-shadow: none !important;
    min-width: 132px !important;
    padding: 0.9rem 1.25rem !important;
    transition: background 0.18s, transform 0.12s !important;
}

#dr-run:hover {
    background: var(--dr-teal-deep) !important;
}

#dr-run:active {
    transform: translateY(1px) scale(0.99) !important;
}

/* === EXAMPLES === */
.dr-examples-label {
    margin: 1.75rem 0 0.7rem;
    font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 0.68rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--dr-muted);
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.dr-examples-label::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--dr-line), transparent);
}

#dr-examples, #dr-examples > div, #dr-examples .wrap, #dr-examples .block {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}

#dr-examples label, #dr-examples .label-wrap, #dr-examples > div > .label-wrap {
    display: none !important;
}

#dr-examples table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    width: auto !important;
    background: transparent !important;
    border: none !important;
}

#dr-examples thead { display: none !important; }
#dr-examples tbody { background: transparent !important; }

#dr-examples tr {
    background: transparent !important;
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 0.55rem !important;
    border: none !important;
}

#dr-examples td, #dr-examples button {
    background: rgba(255, 253, 249, 0.7) !important;
    border: 1px solid var(--dr-line) !important;
    border-radius: 999px !important;
    padding: 0.55rem 0.95rem !important;
    cursor: pointer !important;
    font-size: 0.88rem !important;
    color: var(--dr-ink) !important;
    margin: 0 !important;
    text-align: left !important;
    box-shadow: none !important;
    transition: border-color 0.15s, background 0.15s, transform 0.12s !important;
}

#dr-examples td:hover, #dr-examples button:hover {
    border-color: var(--dr-teal) !important;
    background: rgba(15, 118, 110, 0.08) !important;
    color: var(--dr-teal-deep) !important;
    transform: translateY(-1px);
}

/* === REPORT === */
#dr-report {
    margin-top: 2rem !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--dr-ink) !important;
    min-height: 48px;
}

#dr-report > div, #dr-report .prose {
    background: transparent !important;
    color: var(--dr-ink) !important;
}

#dr-report:not(:empty) {
    background: var(--dr-surface-solid) !important;
    border: 1px solid rgba(20, 33, 43, 0.08) !important;
    border-radius: 20px !important;
    padding: 1.6rem 1.5rem 1.85rem !important;
    box-shadow: 0 22px 50px -36px rgba(20, 33, 43, 0.5) !important;
}

#dr-report h1 {
    font-family: "Fraunces", Georgia, serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--dr-ink);
    margin: 0.4rem 0 0.9rem;
    letter-spacing: -0.02em;
    border-bottom: 2px solid rgba(15, 118, 110, 0.25);
    padding-bottom: 0.55rem;
}

#dr-report h2 {
    font-family: "Fraunces", Georgia, serif;
    font-size: 1.28rem;
    color: var(--dr-teal-deep);
    font-weight: 700;
    margin-top: 1.6rem;
}

#dr-report h3 {
    font-size: 1.05rem;
    font-weight: 700;
    margin-top: 1.25rem;
    color: var(--dr-ink);
}

#dr-report p {
    line-height: 1.75;
    font-size: 1.02rem;
}

#dr-report a {
    color: var(--dr-teal);
    text-decoration: underline;
    text-decoration-thickness: 1.5px;
    text-underline-offset: 3px;
}

#dr-report a:hover { color: var(--dr-teal-deep); }

#dr-report code {
    font-family: "JetBrains Mono", ui-monospace, monospace;
    background: #eef3f4;
    border: 1px solid var(--dr-line);
    padding: 0.12rem 0.4rem;
    font-size: 0.9em;
    border-radius: 6px;
}

#dr-report pre {
    background: #eef3f4;
    border: 1px solid var(--dr-line);
    border-radius: 12px;
    padding: 1rem 1.1rem;
}

#dr-report blockquote {
    border-left: 3px solid var(--dr-teal) !important;
    background: rgba(15, 118, 110, 0.06);
    padding: 0.85rem 1.1rem;
    margin: 1rem 0;
    border-radius: 0 10px 10px 0;
}

#dr-report ul, #dr-report ol { padding-left: 1.35rem; }
#dr-report li { margin: 0.28rem 0; line-height: 1.65; }

#dr-report table {
    border-collapse: collapse;
    width: 100%;
    border: 1px solid var(--dr-line);
    border-radius: 10px;
    overflow: hidden;
}

#dr-report th, #dr-report td {
    border: 1px solid var(--dr-line);
    padding: 0.55rem 0.8rem;
    text-align: left;
}

#dr-report th {
    background: #eef3f4;
    font-weight: 700;
    color: var(--dr-teal-deep);
}

footer { display: none !important; }

@media (max-width: 700px) {
    .gradio-container { padding: 1.5rem 1rem 3rem !important; }
    .dr-query-row { flex-direction: column !important; }
    #dr-run { width: 100% !important; }
    .dr-orb { display: none; }
}
"""

JS = """
() => {
    const focus = () => {
        const el = document.querySelector("#dr-query textarea, #dr-query input");
        if (el) { el.focus(); return true; }
        return false;
    };
    if (!focus()) {
        let tries = 0;
        const i = setInterval(() => {
            if (focus() || ++tries > 20) clearInterval(i);
        }, 100);
    }
}
"""
