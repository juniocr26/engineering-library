export async function BackendStatus() {
  let available = false;
  try {
    const response = await fetch(`${process.env.BACKEND_URL ?? 'http://backend:3000'}/up`, {
      cache: 'no-store', signal: AbortSignal.timeout(3000),
    });
    available = response.ok;
  } catch { /* The reading page remains available during backend downtime. */ }
  return <p className="status"><span aria-hidden="true" className={available ? 'dot online' : 'dot'} />
    {available ? 'Library API connected' : 'Library API temporarily unavailable'}</p>;
}
