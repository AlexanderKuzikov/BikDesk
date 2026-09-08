import { useCallback, useEffect, useState } from 'react';
import { AuthError, api, type Card, type Column, type User } from './api';
import Board from './Board';
import Calendar from './Calendar';
import CardModalHost from './CardModal';
import Docs from './Docs';

export default function App() {
  const [me, setMe] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [columns, setColumns] = useState<Column[]>([]);
  const [cards, setCards] = useState<Card[]>([]);
  const [err, setErr] = useState('');
  const [ready, setReady] = useState(false);
  const [view, setView] = useState<'board' | 'cal' | 'docs'>('board');
  const [openId, setOpenId] = useState<string | null>(null);
  const [docPath, setDocPath] = useState<string | null>(null);
  const [ver, setVer] = useState('');
  const [board, setBoard] = useState('');

  const load = useCallback(async () => {
    const [u, cols, list] = await Promise.all([api.users().catch(() => [] as User[]), api.columns(), api.cards()]);
    setUsers(u);
    setColumns(cols);
    setCards(list);
  }, []);

  useEffect(() => {
    api
      .me()
      .then((u) => {
        setMe(u);
        return load();
      })
      .catch((e: unknown) => {
        if (!(e instanceof AuthError)) setErr(e instanceof Error ? e.message : String(e));
      })
      .finally(() => setReady(true));
    fetch(`${import.meta.env.BASE_URL}api/health`, { credentials: 'same-origin' })
      .then((r) => r.json())
      .then((j: unknown) => {
        const v = (j as { version?: unknown }).version;
        if (typeof v === 'string') setVer(v);
        const b = (j as { board?: unknown }).board;
        if (typeof b === 'string' && b.trim() !== '') setBoard(b.trim());
      })
      .catch(() => undefined);
  }, [load]);

  if (!ready || !me) {
    return (
      <div className="wrap narrow">
        <h1>EchoTracker</h1>
        {err ? <div className="error">{err}</div> : 'Загрузка…'}
      </div>
    );
  }

  return (
    <div className="wrap">
      <header className="topbar">
        <strong><span className="logodot" />EchoTracker</strong>
        {ver !== '' && (
          <span className="muted" title="версия api — если её нет, фронт старый, обновись">
            v{ver}
          </span>
        )}
        {board !== '' && <span className="boardname">{board}</span>}
        <span className="viewswitch">
          <button className={view === 'board' ? 'on' : ''} onClick={() => setView('board')}>Доска</button>
          <button className={view === 'cal' ? 'on' : ''} onClick={() => setView('cal')}>Календарь</button>
          <button className={view === 'docs' ? 'on' : ''} onClick={() => setView('docs')}>Документы</button>
        </span>
      </header>
      {err && <div className="error">{err}</div>}
      {view === 'board' && (
        <Board user={me} columns={columns} cards={cards} reload={() => load().catch(() => undefined)} setOpenId={setOpenId} />
      )}
      {view === 'cal' && <Calendar cards={cards} onOpen={setOpenId} />}
      {view === 'docs' && <Docs initialPath={docPath} onOpenCard={(id) => { setView('board'); setOpenId(id); }} />}
      {openId && (
        <CardModalHost
          cardId={openId}
          users={users}
          columns={columns}
          onClose={() => { setOpenId(null); load().catch(() => undefined); }}
          onOpenDoc={(p) => { setDocPath(p); setView('docs'); }}
        />
      )}
    </div>
  );
}
