export interface PolicyEvaluationResult {
  decision: 'ALLOW' | 'REVIEW' | 'BLOCK';
  risk_score: number;
  policy_version: string;
}
