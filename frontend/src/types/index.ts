export interface ChatConfig {
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  theme?: 'light' | 'dark' | 'auto';
  primaryColor?: string;
  welcomeMessage?: string;
  placeholder?: string;
  enableStreaming?: boolean;
  enableHistory?: boolean;
  userId?: string;
  sessionId?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  isStreaming?: boolean;
  error?: boolean;
}

export interface StreamChunk {
  type: 'chunk' | 'done' | 'error' | 'connected' | 'sources';
  content?: string;
  message?: string;
  done?: boolean;
  error?: string;
  sources?: RAGSource[];
}

export interface RAGSource {
  id: string;
  title: string;
  content: string;
  score: number;
  url?: string;
  page?: number;
}

export type ChatPosition = 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
export type ChatTheme = 'light' | 'dark' | 'auto';