# Final adversarial and minimality review

## Ponytail minimality pass

- The hosted release has one golden path and three audited variants; public-repository execution does not exist.
- Core analysis and validation reuse Python's AST, subprocess, tempfile, hashlib, JSON, difflib, and SQLite modules.
- Streamlit is the only runtime UI dependency; pytest is development-only.
- The unused lockfile was removed. The approved candidate now differs from the baseline by only the requested normalization expression.
- Validation, path containment, structured failures, accessibility cues, and evidence provenance were retained even where they cost additional code.

## Grill-me-style objections and conservative answers

| Objection | Evidence-backed answer or limit |
| --- | --- |
| Is this another repository chatbot? | No. The demo produces deterministic AST evidence, executes named behavior checks, rejects a plausible bad patch, accepts the narrow patch, and exports a review pack. |
| Does acceptance prove semantic equivalence? | No. It proves only the named observations, and the UI and evidence say so. |
| Can the hosted app execute a pasted repository? | No. Execution is allowlisted to the bundled fixture; GitHub import is out of scope. |
| Is the call graph complete? | No. It is static and intentionally reports dynamic-dispatch limitations. |
| Is subprocess isolation an OS sandbox? | No. It adds a timeout, isolated interpreter mode, temporary workspace, bounded output, and an empty environment, but it is not a container boundary. |
| Is IBM Bob actually running in the public app? | No. The repository supplies role guidance and an actor–critic workflow designed for Bob's full-repository context. A real Bob session export remains a human-in-the-loop requirement. |
| What makes the evidence trustworthy? | Candidate, baseline, validator, and runner hashes plus the real unified diff bind the verdict to inspected inputs and evaluator code. |
| What can fail during judging? | Public hosting or networking. The deterministic CLI and bundled fixture remain the fallback; URLs and screenshots must not be claimed until verified. |

## Unresolved human-in-the-loop items

1. Run the workflow in an accessible IBM Bob IDE and add redacted session exports if the submission requires runtime proof.
2. Confirm the public GitHub repository creation and deployment through the account-authorized publishing flow.
3. Capture screenshots only from the verified public deployment.
4. Decide whether the visually checked one-page PDF also requires formal tagged-PDF accessibility remediation.

These items are deliberately unresolved rather than self-authorized or fabricated.
