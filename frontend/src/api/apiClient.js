export const API_BASE_URL = "http://127.0.0.1:8000";

export async function getMessage() {
  const res = await fetch(`${API_BASE_URL}/`);
  return res.json();
}
