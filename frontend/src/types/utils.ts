export interface Request {
  isLoading: boolean;
  result: string | null;
  error: boolean;
}

export interface DraftRequest {
  isLoading: boolean;
  result: string | null;
  error: boolean;
  thinks: string[];
  isThinking: boolean;
}
