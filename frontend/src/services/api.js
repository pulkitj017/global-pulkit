// Default to backend running on 8001 (dev) to match project setup.
// You can override with VITE_API_URL in your .env if needed.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

export async function sendQuery(question) {
  const url = `${API_URL}/query?q=${encodeURIComponent(question)}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}

