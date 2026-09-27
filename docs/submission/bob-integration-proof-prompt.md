# Bob-native integration proof run (instructions, not a transcript)

Use the event branch `bob-2.0-build-2026-09-25` in your local IBM Bob IDE. Pull the integration patch before this run. Confirm `.bob/skills/shadowspec-behavior-gate/SKILL.md` is visible under Bob Settings > Skills and that Bob is in Advanced mode. Approve the skill activation if prompted. For MCP proof, install `requirements-mcp.in`, create your *local* `.bob/mcp.json` from the README example with your actual absolute paths, turn on "Use MCP Servers," and reload servers. Don't commit the machine-specific configuration or secrets.

Paste this prompt into Bob:

> Use the ShadowSpec behavior gate skill. Check this repo's audited SAVE10 fixture with the bad and narrow candidates. If the `shadowspec` MCP server is connected, invoke `validate_fixture` with `candidate="bad"` and then `candidate="narrow"`. In either case, also run the real ShadowSpec CLI once for each candidate. Print each actual verdict, the characterization and acceptance booleans, named failed checks, and source hashes. The rejected CLI's exit code 2 is expected. If the skill or MCP tool isn't available, say exactly which part failed. Do not edit fixture sources or claim arbitrary-patch validation.

After the run, export the actual Bob task/session as Markdown via Bob's export control; save it under `bob_sessions/` with a date/topic filename. Save a screenshot of Bob's tool calls and outputs if available. Follow `bob_sessions/README.md` to redact tokens, local absolute paths and unrelated details. Add an honest row to `bob_sessions/MANIFEST.md`: label Skill, MCP and CLI separately as observed or not observed. If Bob did not make both tool calls, do not substitute this prompt or local MCP smoke-test for a real Bob transcript.
