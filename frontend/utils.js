const API = "http://127.0.0.1:8000";

export function setAccessToken(t) { sessionStorage.setItem('access', t); }
export function getAccessToken() { return sessionStorage.getItem('access'); }
export function setRefreshToken(t) { sessionStorage.setItem('refresh', t); }
export function getRefreshToken() { return sessionStorage.getItem('refresh'); }

export async function requestJSON(url, opts = {}) {
  opts.headers = opts.headers || {};
  const a = getAccessToken();
  if (a) opts.headers['Authorization'] = 'Bearer ' + a; 
  if (opts.body && typeof opts.body === 'object')
    opts.body = JSON.stringify(opts.body);
  if (!opts.headers['Content-Type'])
    opts.headers['Content-Type'] = 'application/json';

  const resp = await fetch(url, opts);
  let data = null;
  try { data = await resp.json(); } catch { data = null; }
  return { ok: resp.ok, status: resp.status, data };
}
