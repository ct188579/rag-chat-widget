import { useState, useCallback, useRef } from 'react';
import { ChatConfig, Message, StreamChunk } from '../types';
import APIClient from '../services/api';
import { WebSocketManager } from '../services/websocket';

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  isOpen: boolean;
  sendMessage: (content: string) => Promise<void>;
  toggleOpen: () => void;
  clearMessages: () => void;
  regenerateMessage: (messageId: string) => Promise<void>;
}

export function useChat(config: ChatConfig): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>(() => {
    if (config.welcomeMessage) {
      return [{
        id: 'welcome',
        role: 'assistant',
        content: config.welcomeMessage,
        timestamp: Date.now(),
      }];
    }
    return [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const wsManagerRef = useRef<WebSocketManager | null>(null);

  const apiClient = useRef(new APIClient());

  const addMessage = useCallback((message: Message) => {
    setMessages(prev => [...prev, message]);
  }, []);

  const updateMessage = useCallback((id: string, updates: Partial<Message>) => {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, ...updates } : m));
  }, []);

  const sendViaHTTP = useCallback(async (content: string, assistantId: string) => {
    try {
      const response = await apiClient.current.sendMessage(content, messages);
      updateMessage(assistantId, {
        content: response.answer,
        isStreaming: false,
      });
    } catch (error) {
      updateMessage(assistantId, {
        content: '抱歉，服务暂时不可用，请稍后重试。',
        error: true,
        isStreaming: false,
      });
    }
  }, [messages, updateMessage]);

  const sendViaWebSocket = useCallback(async (content: string, assistantId: string) => {
    const wsManager = new WebSocketManager(config.sessionId);
    wsManagerRef.current = wsManager;

    return new Promise<void>((resolve, reject) => {
      let fullContent = '';

      wsManager.onMessage((chunk: StreamChunk) => {
        if (chunk.type === 'chunk' && chunk.content) {
          fullContent += chunk.content;
          updateMessage(assistantId, {
            content: fullContent,
            isStreaming: true,
          });
        } else if (chunk.type === 'done') {
          updateMessage(assistantId, { isStreaming: false });
          wsManager.disconnect();
          resolve();
        }
      });

      wsManager.onError((error) => {
        updateMessage(assistantId, {
          content: '连接失败，请检查网络。',
          error: true,
          isStreaming: false,
        });
        reject(error);
      });

      wsManager.connect()
        .then(() => {
          wsManager.send(content);
        })
        .catch(reject);
    });
  }, [config.sessionId, updateMessage]);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: Date.now(),
    };

    const assistantId = `assistant_${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      isStreaming: true,
    };

    addMessage(userMessage);
    addMessage(assistantMessage);
    setIsLoading(true);

    try {
      if (config.enableStreaming) {
        await sendViaWebSocket(content, assistantId);
      } else {
        await sendViaHTTP(content, assistantId);
      }
    } catch (error) {
      updateMessage(assistantId, {
        content: '抱歉，服务暂时不可用。',
        error: true,
        isStreaming: false,
      });
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, config.enableStreaming, addMessage, updateMessage, sendViaHTTP, sendViaWebSocket]);

  const regenerateMessage = useCallback(async (messageId: string) => {
    const targetIndex = messages.findIndex(m => m.id === messageId);
    if (targetIndex <= 0) return;

    const userMessage = messages[targetIndex - 1];
    if (userMessage.role !== 'user') return;

    setMessages(prev => prev.slice(0, targetIndex));
    await sendMessage(userMessage.content);
  }, [messages, sendMessage]);

  const toggleOpen = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages(config.welcomeMessage ? [{
      id: 'welcome',
      role: 'assistant',
      content: config.welcomeMessage,
      timestamp: Date.now(),
    }] : []);
  }, [config.welcomeMessage]);

  return {
    messages,
    isLoading,
    isOpen,
    sendMessage,
    toggleOpen,
    clearMessages,
    regenerateMessage,
  };
}