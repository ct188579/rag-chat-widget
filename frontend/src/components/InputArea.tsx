import React, { useState, useRef, useCallback } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface InputAreaProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export const InputArea: React.FC<InputAreaProps> = ({
  onSend,
  isLoading,
  placeholder = '输入消息...',
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [input, isLoading, onSend]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = e.target.scrollHeight + 'px';
  }, []);

  return (
    <div className="aiw-input-area">
      <textarea
        ref={textareaRef}
        className="aiw-textarea"
        value={input}
        onChange={handleInput}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={1}
        disabled={isLoading}
      />

      <button
        className="aiw-input-btn aiw-send-btn"
        onClick={handleSend}
        disabled={!input.trim() || isLoading}
      >
        {isLoading ? (
          <Loader2 size={20} className="aiw-spin" />
        ) : (
          <Send size={20} />
        )}
      </button>
    </div>
  );
};

export default InputArea;