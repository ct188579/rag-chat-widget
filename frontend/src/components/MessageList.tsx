import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../types';
import { User, Bot, AlertCircle } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages]);

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div ref={scrollRef} className="aiw-messages">
      {messages.length === 0 && (
        <div className="aiw-empty">
          <Bot size={48} className="aiw-empty-icon" />
          <p>开始对话吧</p>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`aiw-msg ${message.role === 'user' ? 'aiw-msg-user' : 'aiw-msg-assistant'}`}
        >
          <div className="aiw-avatar">
            {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
          </div>

          <div className="aiw-msg-content">
            <div className="aiw-bubble">
              {message.error ? (
                <div className="aiw-error">
                  <AlertCircle size={16} />
                  <span>{message.content}</span>
                </div>
              ) : message.role === 'assistant' ? (
                <ReactMarkdown>{message.content || '思考中...'}</ReactMarkdown>
              ) : (
                <p>{message.content}</p>
              )}

              {message.isStreaming && (
                <span className="aiw-cursor">▊</span>
              )}
            </div>

            <span className="aiw-time">{formatTime(message.timestamp)}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;