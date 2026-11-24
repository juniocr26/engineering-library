'use client';
import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ProjectList } from './project-list';
import { CatalogState } from './catalog-state';
import type { Project } from '@/lib/catalog';
import type { Language } from '@/lib/i18n';

type Operation = { id: string; action?: string; state: string; phase: string; error?: string };
type Selection = { action: 'add' | 'update' | 'remove'; project?: Project };
type Directory = { id?: string; directory: string; collection: number; name?: string; slug?: string; status: 'ready' | 'registered' | 'unavailable' };
const finished = (operation: Operation) => ['completed', 'error', 'interrupted'].includes(operation.state);

export function CatalogManager({ projects, language, page, enabled }: { projects: Project[]; language: Language; page: number; enabled: boolean }) {
  const en = language === 'en';
  const router = useRouter();
  const dialog = useRef<HTMLDialogElement>(null);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [operation, setOperation] = useState<Operation | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(false);
  const [directories, setDirectories] = useState<Directory[]>([]);
  const [directoriesLoading, setDirectoriesLoading] = useState(false);
  const [directoryError, setDirectoryError] = useState<string | null>(null);
  const autofilled = useRef({ name: '', slug: '' });
  const busy = submitting || !!(operation && !finished(operation));
  const phases: Record<string, string> = en ? {
    queued: 'Waiting for MakeDocs…', validating: 'Validating source and ownership…', starting: 'Starting MakeDocs…',
    'validating-ownership': 'Checking document ownership…', 'evidence-collected': 'Source evidence collected…', generating: 'Generating documentation…', publishing: 'Publishing documentation…', written: 'Documentation written…', 'no-op': 'Documentation is current…', removing: 'Removing project from the library…', completed: 'Operation completed.', error: 'The operation failed. Documentation and recovery evidence were preserved.', interrupted: 'The operation was interrupted. Recovery evidence was preserved.',
  } : {
    queued: 'Aguardando o MakeDocs…', validating: 'Validando origem e arquivos administrados…', starting: 'Iniciando o MakeDocs…',
    'validating-ownership': 'Verificando arquivos documentais…', 'evidence-collected': 'Evidências da origem coletadas…', generating: 'Gerando documentação…', publishing: 'Publicando documentação…', written: 'Documentação gravada…', 'no-op': 'A documentação está atualizada…', removing: 'Removendo projeto da biblioteca…', completed: 'Operação concluída.', error: 'A operação falhou. A documentação e as evidências de recuperação foram preservadas.', interrupted: 'A operação foi interrompida. As evidências de recuperação foram preservadas.',
  };

  useEffect(() => {
    if (selection && !dialog.current?.open) dialog.current?.showModal();
    if (!selection && dialog.current?.open) dialog.current.close();
  }, [selection]);

  useEffect(() => {
    if (!enabled) return;
    let disposed = false;
    fetch('/api/catalog-management', { cache: 'no-store' }).then(response => response.ok ? response.json() : null).then(data => {
      if (!disposed && data?.operation && !finished(data.operation)) {
        setOperation(data.operation);
        setSelection({ action: data.operation.action ?? 'update' });
      }
    }).catch(() => {});
    return () => { disposed = true; };
  }, [enabled]);

  const selectingDirectory = selection?.action === 'add' && !operation;
  useEffect(() => {
    if (!selectingDirectory) return;
    const controller = new AbortController();
    fetch('/api/catalog-management/directories', { cache: 'no-store', signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error('Unavailable');
      const data = await response.json();
      if (!controller.signal.aborted) setDirectories(data.directories);
    }).catch(() => {
      if (!controller.signal.aborted) setDirectoryError('listing_unavailable');
    }).finally(() => {
      if (!controller.signal.aborted) setDirectoriesLoading(false);
    });
    return () => controller.abort();
  }, [selectingDirectory]);

  const operationId = operation?.id;
  const terminal = operation ? finished(operation) : true;
  useEffect(() => {
    if (!operationId || terminal) return;
    let disposed = false;
    let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      try {
        const response = await fetch(`/api/catalog-management/${operationId}`, { cache: 'no-store', signal: AbortSignal.timeout(10000) });
        if (!response.ok) throw new Error('Unavailable');
        const data = await response.json();
        if (!disposed && data.operation) {
          setError(false);
          setOperation(data.operation);
          if (finished(data.operation)) { router.refresh(); return; }
        }
      } catch { if (!disposed) setError(true); }
      if (!disposed) timer = setTimeout(poll, 1000);
    };
    timer = setTimeout(poll, 300);
    return () => { disposed = true; clearTimeout(timer); };
  }, [operationId, terminal, router]);

  function choose(next: Selection) {
    setOperation(null);
    setError(false);
    setSelection(next);
    if (next.action === 'add') {
      setDirectories([]);
      setDirectoriesLoading(true);
      setDirectoryError(null);
      autofilled.current = { name: '', slug: '' };
    }
  }

  function directoryChanged(event: React.ChangeEvent<HTMLSelectElement>) {
    const directory = directories.find(item => item.id === event.currentTarget.value);
    setDirectoryError(null);
    if (!directory || directory.status !== 'ready') return;
    for (const key of ['name', 'slug'] as const) {
      const input = event.currentTarget.form?.elements.namedItem(key);
      if (input instanceof HTMLInputElement && (!input.value.trim() || input.value === autofilled.current[key])) {
        input.value = directory[key] ?? '';
        autofilled.current[key] = input.value;
      }
    }
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selection || busy || operation) return;
    const form = new FormData(event.currentTarget);
    const body = selection.action === 'add' ? Object.fromEntries(form) : { id: selection.project?.id };
    setSubmitting(true);
    setError(false);
    try {
      const response = await fetch(`/api/catalog-management/${selection.action}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: AbortSignal.timeout(15000) });
      if (!response.ok) {
        const data = await response.json().catch(() => null);
        if (selection.action === 'add' && ['source_unavailable', 'project_exists'].includes(data?.error)) {
          setDirectoryError(data.error);
          return;
        }
        throw new Error('Rejected');
      }
      const data = await response.json();
      setOperation(data.operation);
    } catch { setError(true); }
    finally { setSubmitting(false); }
  }

  const add = en ? 'Add project' : 'Adicionar projeto';
  const title = selection?.action === 'add' ? add : selection?.action === 'remove' ? (en ? 'Remove project' : 'Remover projeto') : (en ? 'Update documentation' : 'Atualizar documentação');
  return <>
    {projects.length ? <ProjectList projects={projects} language={language} page={page} onAction={enabled ? (action, project) => choose({ action, project }) : undefined}/> : <CatalogState kind="empty" language={language}/>}
    {enabled && <div className="catalog-add"><button type="button" className="lang" onClick={() => choose({ action: 'add' })}>{add}</button></div>}
    <dialog ref={dialog} className="catalog-dialog" aria-labelledby="catalog-dialog-title" onCancel={event => { if (busy) event.preventDefault(); else setSelection(null); }} onClose={() => { if (!busy) setSelection(null); }}>
      <form onSubmit={submit}>
        <h2 id="catalog-dialog-title">{title}</h2>
        {selection?.project && <p><strong>{selection.project.name}</strong></p>}
        {!operation && selection?.action === 'add' && <fieldset disabled={busy}>
          <label>{en ? 'Project name' : 'Nome do projeto'}<input name="name" required maxLength={120} autoFocus/></label>
          <label>{en ? 'Documentation slug' : 'Slug documental'}<input name="slug" required pattern="[a-z0-9]+(-[a-z0-9]+)*" maxLength={100} placeholder="meu-projeto"/></label>
          <label>{en ? 'Project folder' : 'Pasta do projeto'}<select name="sourceSelection" required defaultValue="" disabled={directoriesLoading || !!(directoryError === 'listing_unavailable')} aria-describedby="catalog-source-help" onChange={directoryChanged}>
            <option value="" disabled>{directoriesLoading ? (en ? 'Loading folders…' : 'Carregando pastas…') : (en ? 'Choose a folder…' : 'Escolher pasta…')}</option>
            {[...new Set(directories.map(item => item.collection))].map(collection => <optgroup key={collection} label={`${en ? 'Collection' : 'Coleção'} ${collection}`}>
              {directories.filter(item => item.collection === collection).map(item => <option key={`${collection}:${item.directory}`} value={item.id ?? ''} disabled={item.status !== 'ready'}>{item.directory}{item.status === 'registered' ? (en ? ' — already registered' : ' — já cadastrado') : item.status === 'unavailable' ? (en ? ' — unavailable for documentation' : ' — indisponível para documentação') : ''}</option>)}
            </optgroup>)}
          </select></label>
          <p id="catalog-source-help" role={directoryError ? 'alert' : undefined}>{directoryError === 'listing_unavailable' ? (en ? 'Unable to load the permitted folders. Close and reopen this dialog to try again.' : 'Não foi possível carregar as pastas permitidas. Feche e reabra este modal para tentar novamente.') : directoryError === 'project_exists' ? (en ? 'This project is already registered. Choose another folder.' : 'Este projeto já está cadastrado. Escolha outra pasta.') : directoryError === 'source_unavailable' ? (en ? 'The selected folder or documentation destination is no longer accessible. Close and reopen this dialog to reload the folders.' : 'A pasta selecionada ou seu destino documental não está mais acessível. Feche e reabra este modal para recarregar as pastas.') : !directoriesLoading && !directories.some(item => item.status === 'ready') ? (en ? 'No folders are currently available to add. Registered or inaccessible folders cannot be selected.' : 'Não há pastas disponíveis para adicionar no momento. Pastas cadastradas ou inacessíveis não podem ser selecionadas.') : (en ? 'Only permitted folders accessible to MakeDocs are listed. Source files are not uploaded.' : 'A seleção usa as pastas permitidas e acessíveis ao MakeDocs. Os arquivos de origem não são enviados pelo navegador.')}</p>
        </fieldset>}
        {!operation && selection?.action === 'update' && <p>{en ? 'Do you want to update the documentation for this project?' : 'Você deseja atualizar a documentação deste projeto?'}</p>}
        {!operation && selection?.action === 'remove' && <p>{en ? 'Do you want to remove this project from Engineering Library? Its catalog entry and library documentation will be removed. The original source code will be preserved.' : 'Você deseja remover este projeto da Engineering Library? O registro do catálogo e sua documentação na biblioteca serão removidos. O código-fonte original será preservado.'}</p>}
        {(busy || operation) && <div className="catalog-progress" role="status" aria-live="polite"><p>{operation ? phases[operation.phase] ?? phases.validating : phases.queued}</p>{busy && <progress aria-label={en ? 'MakeDocs progress' : 'Progresso do MakeDocs'}/>}</div>}
        {operation?.error === 'source_unavailable' && <p role="alert">{en ? 'The source or its documentation mount is unavailable. Check the existing MakeDocs mounts.' : 'A origem ou seu mount documental está indisponível. Verifique os mounts existentes do MakeDocs.'}</p>}
        {error && <p role="alert">{en ? 'Unable to confirm the operation. Check the source reference, duplicates, and local permissions. A running operation may still finish.' : 'Não foi possível confirmar a operação. Verifique a referência de origem, duplicações e permissões locais. Uma operação em andamento ainda poderá terminar.'}</p>}
        <div className="catalog-dialog-actions">
          {!operation && <button className="lang" type="submit" disabled={busy || (selection?.action === 'add' && (directoriesLoading || directoryError === 'listing_unavailable'))}>{selection?.action === 'add' ? add : selection?.action === 'remove' ? (en ? 'Yes, remove' : 'Sim, remover') : (en ? 'Yes, update' : 'Sim, atualizar')}</button>}
          <button className="lang" type="button" disabled={busy} onClick={() => setSelection(null)}>{operation ? (en ? 'Close' : 'Fechar') : (en ? 'Cancel' : 'Cancelar')}</button>
        </div>
      </form>
    </dialog>
  </>;
}
