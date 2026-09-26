export interface CheckResult {
  name: string;
  kind: "characterization" | "acceptance";
  passed: boolean;
}

export interface VerdictData {
  run_id: string;
  candidate: string;
  verdict: "accepted" | "rejected" | "error";
  characterization_passed: boolean;
  acceptance_passed: boolean;
  failed_checks: string[];
  source_sha256: string;
  baseline_sha256: string;
  validator_sha256: string;
  runner_sha256: string;
  output: string;
  checks: CheckResult[];
  diff: string;
  description: string;
  label: string;
  reason: string;
}

export type CandidateKey = "baseline" | "bad" | "narrow";

export const CANDIDATE_META: Record<
  CandidateKey,
  { title: string; subtitle: string }
> = {
  baseline: {
    title: "baseline",
    subtitle: "Original — no whitespace trimming",
  },
  bad: {
    title: "bad",
    subtitle: "strip().upper() — breaks case sensitivity",
  },
  narrow: {
    title: "narrow",
    subtitle: "strip() only — correct minimal fix",
  },
};
