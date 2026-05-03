import { StreamChunk } from '../types';

const WS_ENDPOINT = import.meta.env.VITE_WS_ENDPOINT || 'ws://localhost:8000/ws/chat';

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private sessionId?: string;
  private messageCallback: ((chunk: StreamChunk) => void) | null = null;
  private errorCallback: ((error: Error) => void) | null = null;
  private closeCallback: (() => void) | null = null;

  constructor(sessionId?: string) {
    this.sessionId = sessionId;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(WS_ENDPOINT);

        this.ws.onopen = () => {
        };

        this.ws.onmessage = (event) => {
          try {
            const data: StreamChunk = JSON.parse(event.data);
            
            if (data.type === 'connected') {
              resolve();
              return;
            }
            
            if (data.type === 'error') {
              this.errorCallback?.(new Error(data.message || 'Unknown error'));
              return;
            }
            
            this.messageCallback?.(data);
          } catch {
            this.errorCallback?.(new Error('Failed to parse WebSocket message'));
          }
        };

        this.ws.onerror = () => {
          reject(new Error('WebSocket connection failed'));
        };

        this.ws.onclose = () => {
          this.closeCallback?.();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  send(message: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    this.ws.send(JSON.stringify({
      type: 'chat',
      message,
      session_id: this.sessionId,
      enable_rag: true,
      stream: true,
    }));
  }

  onMessage(callback: (chunk: StreamChunk) => void): void {
    this.messageCallback = callback;
  }

  onError(callback: (error: Error) => void): void {
    this.errorCallback = callback;
  }

  onClose(callback: () => void): void {
    this.closeCallback = callback;
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

export default WebSocketManager;