import { Message } from '../types';

const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || 'http://localhost:8000/api/v1';

class APIClient {
  async sendMessage(message: string, history: Message[]): Promise<{ answer: string }> {
    const response = await fetch(`${API_ENDPOINT}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        history: history.map(m => ({ role: m.role, content: m.content })),
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

export default APIClient;