import React from 'react';
import { ChatConfig } from '../types';
import { ChatWindow } from './ChatWindow';
import { useChat } from '../hooks/useChat';
import { MessageCircle, X } from 'lucide-react';

interface ChatWidgetProps {
  config: ChatConfig;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({ config }) => {
  const { isOpen, toggleOpen } = useChat(config);

  const positionClass = {
    'bottom-right': 'aiw-br',
    'bottom-left': 'aiw-bl',
    'top-right': 'aiw-tr',
    'top-left': 'aiw-tl',
  }[config.position || 'bottom-right'];

  return (
    <div className={`aiw-widget ${positionClass}`}>
      <button
        className="aiw-toggle"
        onClick={toggleOpen}
        style={{ backgroundColor: config.primaryColor || '#3b82f6' }}
        aria-label={isOpen ? '关闭聊天' : '打开聊天'}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {isOpen && (
        <div className="aiw-window">
          <ChatWindow config={config} onClose={toggleOpen} />
        </div>
      )}
    </div>
  );
};

export default ChatWidget;