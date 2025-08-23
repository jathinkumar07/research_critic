export interface Citation {
  reference: string;
  valid: boolean;
}

export interface FactCheckResult {
  claim: string;
  status: string;
}

export interface AnalysisStats {
  word_count: number;
  plagiarism_percent: number;
  citations_count: number;
}

export interface AnalysisResponse {
  summary: string;
  plagiarism: number;
  citations: Citation[];
  fact_check: {
    facts: FactCheckResult[];
  };
  stats: AnalysisStats;
}

export interface ApiError {
  error: string;
}