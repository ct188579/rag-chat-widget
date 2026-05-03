import React from 'react';
import { ChatConfig } from '../types';
import { useChat } from '../hooks/useChat';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { Trash2, X } from 'lucide-react';

interface ChatWindowProps {
  config: ChatConfig;
  onClose: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ config, onClose }) => {
  const {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
  } = useChat(config);

  return (
    <div className="aiw-main" data-theme={config.theme || 'auto'}>
      <div className="aiw-header" style={{ 
        backgroundColor: config.primaryColor || '#3b82f6' 
      }}>
        <div className="aiw-header-title">
          <span>AI 助手</span>
        </div>
        <div className="aiw-header-actions">
          <button 
            className="aiw-header-btn"
            onClick={clearMessages}
            title="清空对话"
          >
            <Trash2 size={18} />
          </button>
          <button 
            className="aiw-header-btn"
            onClick={onClose}
            title="关闭"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      <MessageList messages={messages} />

      <InputArea
        onSend={sendMessage}
        isLoading={isLoading}
        placeholder={config.placeholder}
      />
    </div>
  );
};

export default ChatWindow;