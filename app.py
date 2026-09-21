from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import streamlit as st

# Streamlit runs this source-tree entry point without installing the ``src``
# layout package. Keep local launches and clean deployments importable without
# requiring a global PYTHONPATH setting.
SRC_ROOT = Path(__file__).resolve().parent / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from shadowspec.service import run_demo


LOGGER = logging.getLogger(__name__)


st.set_page_config(page_title="ShadowSpec", page_icon="◐", layout="wide")
st.markdown(
    """
    <style>
    :root {
      --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
      --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
      --accent: #c7ff4a;
      --surface: #11151a;
      --border: #626b77;
      --muted: #b8bdc7;
    }
    .stApp { background: #0b0d10; color: #f4f1e8; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1180px; padding-top: 2rem; }
    .stApp p, .stApp label, .stApp button { letter-spacing:.005em; }
    h1 { letter-spacing:-.025em; line-height:1.05; }
    h2 { letter-spacing:-.018em; line-height:1.12; }
    h3 { letter-spacing:-.01em; line-height:1.18; }
    .eyebrow { color:var(--accent); text-transform:uppercase; letter-spacing:.12em; font-size:.74rem; font-weight:700; }
    .hero { font-size: clamp(2.4rem, 7vw, 5.8rem); line-height:.94; letter-spacing:-.045em; font-weight:750; margin:.4rem 0 1rem; }
    .lede { color:var(--muted); max-width:740px; font-size:1.08rem; line-height:1.6; letter-spacing:.003em; }
    .proof-flow { display:grid; grid-template-columns:repeat(3, 1fr); gap:.65rem; margin:1.4rem 0 2rem; padding:0; list-style:none; }
    .proof-step { border:1px solid var(--border); background:var(--surface); border-radius:14px; padding:.85rem 1rem; }
    .proof-step strong { display:block; color:#f4f1e8; font-size:.95rem; letter-spacing:-.008em; }
    .proof-step span { color:var(--muted); font-size:.82rem; line-height:1.45; letter-spacing:.006em; }
    .proof-step.bad { border-left:3px solid #ff7474; }
    .proof-step.good { border-left:3px solid var(--accent); }
    .proof-step.safe { border-left:3px solid #7fc8ff; }
    .panel { border:1px solid var(--border); background:var(--surface); border-radius:18px; padding:1.15rem; }
    .contract-heading { color:var(--accent); font-size:.95rem; font-weight:700; margin:1rem 0 .35rem; }
    .contract-heading:first-child { margin-top:0; }
    .delta-token { color:#f4f1e8; font-weight:750; }
    .space-key { color:var(--muted); font-size:.82rem; }
    .boundary { color:#b8bdc7; font-size:.9rem; }
    div[data-testid="stButton"] button,
    div[data-testid="stDownloadButton"] button {
      min-height:44px;
      transition:transform 140ms var(--ease-out), opacity 180ms var(--ease-in-out);
      touch-action:manipulation;
    }
    div[data-testid="stButton"] button { background:var(--accent); color:#10130b; border:0; font-weight:750; }
    div[data-testid="stButton"] button:hover,
    div[data-testid="stDownloadButton"] button:hover { opacity:.9; }
    div[data-testid="stButton"] button:active,
    div[data-testid="stDownloadButton"] button:active { transform:scale(.97); transition-duration:120ms; }
    div[data-testid="stAlert"] { border-radius:12px; }
    div[data-testid="stMetric"] { border-top:1px solid var(--border); padding-top:.75rem; }
    div[role="radiogroup"] { gap:.35rem; }
    :focus-visible { outline:3px solid var(--accent) !important; outline-offset:3px; }
    @media (max-width: 700px) {
      .block-container { padding:1.25rem 1rem 2rem; }
      .hero { line-height:1; }
      .proof-flow { grid-template-columns:1fr; gap:.5rem; margin-bottom:1.4rem; }
      .proof-step { padding:.72rem .85rem; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        scroll-behavior:auto !important;
        transition-duration:.01ms !important;
        animation-duration:.01ms !important;
        animation-iteration-count:1 !important;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">Legacy maintenance evidence workbench</div>', unsafe_allow_html=True)
st.title("ShadowSpec")
st.markdown('<div class="hero">Reject the broad patch.<br>Accept the proof.</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="lede">Freeze observed behavior, test the requested delta separately, and export exactly what a reviewer needs. No API key. No arbitrary hosted execution.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <ol class="proof-flow" aria-label="Judge proof sequence">
      <li class="proof-step bad"><strong><span aria-hidden="true">1 · </span>Reject the bad patch</strong><span>Catch the hidden case-sensitivity regression.</span></li>
      <li class="proof-step good"><strong><span aria-hidden="true">2 · </span>Accept the narrow patch</strong><span>Prove only the requested whitespace delta.</span></li>
      <li class="proof-step safe"><strong><span aria-hidden="true">3 · </span>Export the evidence</strong><span>Diff, hashes, checks, risks, and rollback.</span></li>
    </ol>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1, 1], gap="large")
with left:
    st.subheader("1 · Choose the candidate")
    selected = st.radio(
        "Prepared candidate",
        ("Narrow candidate", "Plausible bad candidate", "Unchanged baseline"),
        help="All candidates are bundled, audited fixtures.",
    )
    descriptions = {
        "Narrow candidate": "Trim surrounding whitespace only. Preserve case sensitivity.",
        "Plausible bad candidate": "Trim and uppercase. Solves the request but silently broadens behavior.",
        "Unchanged baseline": "Preserves behavior but does not satisfy the new request.",
    }
    st.info(descriptions[selected], icon="ℹ️")
    run_clicked = st.button("Run differential proof", type="primary", use_container_width=True)

with right:
    st.subheader("The contract to preserve")
    st.markdown(
        """
        <div class="panel">
          <h4 class="contract-heading">Requested delta</h4>
          <p>Accept <code class="delta-token">␠SAVE10␠</code> while changing nothing else. <span class="space-key">␠ = space</span></p>
          <h4 class="contract-heading">Frozen observations</h4>
          <p>Case sensitivity · pricing · negative-input error · SQLite audit write</p>
          <p class="boundary">“Accepted” means these named observations passed. It is not a universal safety claim.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if run_clicked:
    candidate = {
        "Narrow candidate": "narrow",
        "Plausible bad candidate": "bad",
        "Unchanged baseline": "baseline",
    }[selected]
    try:
        with st.spinner("Running characterization and acceptance checks…"):
            result = run_demo(candidate)
    except Exception:
        LOGGER.exception("Unexpected failure while running prepared candidate %s", candidate)
        st.error("ERROR · Validation could not complete. Please retry or use the local CLI.")
    else:
        st.divider()
        st.subheader("2 · Differential verdict")
        if result.validation.verdict == "accepted":
            st.success("ACCEPTED · preserved behavior and requested delta both pass", icon="✅")
        elif result.validation.verdict == "rejected":
            st.error("REJECTED · the candidate does not satisfy the full contract", icon="⛔")
        else:
            st.error("ERROR · validation did not complete, so no contract verdict was issued", icon="⚠️")

        a, b, c, d = st.columns(4)
        checks_completed = result.validation.verdict != "error"
        a.metric(
            "Characterization",
            "PASS" if result.validation.characterization_passed else "FAIL" if checks_completed else "NOT RUN",
        )
        b.metric(
            "Acceptance",
            "PASS" if result.validation.acceptance_passed else "FAIL" if checks_completed else "NOT RUN",
        )
        c.metric("Files mapped", result.analysis["file_count"])
        d.metric("Run ID", result.validation.run_id)

        if result.validation.failed_checks:
            label = "Run issue" if result.validation.verdict == "error" else "Failed checks"
            st.warning(label + ": " + ", ".join(result.validation.failed_checks), icon="⚠️")

        try:
            check_results = json.loads(result.validation.output).get("checks", [])
        except (AttributeError, TypeError, ValueError):
            check_results = []
        if check_results:
            st.markdown("#### Check results")
            status_lines = []
            for check in check_results:
                status = "PASS" if check.get("passed") else "FAIL"
                group = "Preserved" if check.get("kind") == "characterization" else "Requested delta"
                status_lines.append(f"- **{status}** — {group}: {check.get('name', 'Unnamed check')}")
            st.markdown("\n".join(status_lines))

        with st.expander("Behavior map and side-effect signals", expanded=True):
            st.write("Functions:", ", ".join(result.analysis["functions"]))
            st.write("Side-effect signals:", ", ".join(result.analysis["side_effects"]))
            st.caption(result.analysis["limitations"][0])

        st.subheader("3 · Reviewer evidence")
        st.download_button(
            "Download Markdown evidence pack",
            result.evidence_markdown,
            file_name=f"shadowspec-{candidate}-{result.validation.run_id}.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.download_button(
            "Download JSON evidence pack",
            result.evidence_json,
            file_name=f"shadowspec-{candidate}-{result.validation.run_id}.json",
            mime="application/json",
            use_container_width=True,
        )
        with st.expander("Preview evidence pack"):
            st.markdown(result.evidence_markdown)

st.divider()
st.caption("Hosted execution is restricted to the bundled audited fixture. Temporary workspaces and timeouts are not an OS-level sandbox.")
