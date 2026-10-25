/** Attempt artifacts can be provisional. Only the canonical summary proves resolution. */
export function isDecisionResolved(summary: { phase?: string | null } | null | undefined): boolean {
  return summary?.phase === 'decision_resolved'
}
