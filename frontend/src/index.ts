import './styles/index.css';

export { ChatWidget } from './components/ChatWidget';
export { ChatWindow } from './components/ChatWindow';
export { MessageList } from './components/MessageList';
export { InputArea } from './components/InputArea';

export { useChat } from './hooks/useChat';

export type {
  ChatConfig,
  Message,
  StreamChunk,
  ChatPosition,
  ChatTheme,
  RAGSource,
} from './types';

export { default as APIClient } from './services/api';
export { WebSocketManager } from './services/websocket';