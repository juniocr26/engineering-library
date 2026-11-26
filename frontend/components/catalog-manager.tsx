'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ProjectList, OperationIndicator } from './project-list';
import { CatalogState } from './catalog-state';
import type { Project } from '@/lib/catalog';
import type { Language } from '@/lib/i18n';

type Operation = { id: string; action?: 'add' | 'update' | 'remove'; projectId?: string; projectName?: string; projectSlug?: string; state: string; phase: string; error?: string; removalReason?: string; notificationAcknowledged?: boolean };
type Selection = { action: 'add' | 'update' | 'remove'; project?: Project };
const finished = (operation: Operation) => ['completed', 'error', 'interrupted'].includes(operation.state);
const removing = (operation: Operation) => operation.action === 'remove' || operation.removalReason === 'source_missing';

export function CatalogManager({ projects, language, page, enabled }: { projects: Project[]; language: Language; page: number; enabled: boolean }) {
  const en = language === 'en';
  const router = useRouter();
  const dialog = useRef<HTMLDialogElement>(null);
  const helpDialog = useRef<HTMLDialogElement>(null);
  const helpButton = useRef<HTMLButtonElement>(null);
  const [helpOpen, setHelpOpen] = useState(false);
  const version = useRef(0);
  const submitGuard = useRef(false);
  const refreshed = useRef(new Set<string>());
  const acknowledged = useRef(new Set<string>());
  const [selection, setSelection] = useState<Selection | null>(null);
  const [trackedProject, setTrackedProject] = useState<Project | undefined>();
  const [operation, setOperation] = useState<Operation | null>(null);
  const [showMissing, setShowMissing] = useState(false);
  const [removed, setRemoved] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(false);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const busy = submitting || !!(operation && !finished(operation));
  const phases: Record<string, string> = en ? {
    completed: 'Operation completed.', error: 'The operation failed. Documentation and recovery evidence were preserved.', interrupted: 'The operation was interrupted. Recovery evidence was preserved.',
  } : {
    completed: 'Operação concluída.', error: 'A operação falhou. A documentação e as evidências de recuperação foram preservadas.', interrupted: 'A operação foi interrompida. As evidências de recuperação foram preservadas.',
  };
  const defaultCommunicationError = en ? 'Unable to confirm the operation. Check the source reference, duplicates, and local permissions. A running operation may still finish.' : 'Não foi possível confirmar a operação. Verifique a referência de origem, duplicações e permissões locais. Uma operação em andamento ainda poderá terminar.';

  const registrationErrors: Record<string, string> = en ? {
    request_conflict: 'This request identifier belongs to another operation. Try again.',
    operation_busy: 'Another operation is running. Wait for it to finish and try again.',
    project_exists: 'A different project is already registered with this directory or identity.',
    source_conflict: 'Another copy of this repository is still accessible. Its existing registration was preserved.',
    source_unavailable: 'The project could not be accessed on the host. Check its path, permissions, and filesystem adapter.',
    catalog_metadata_conflict: 'The existing project metadata needs recovery. Its identity and documentation were preserved.',
    management_unavailable: 'The local management service is unavailable. Check application startup.',
  } : {
    request_conflict: 'Esta solicitação já pertence a outra operação. Tente novamente.',
    operation_busy: 'Outra operação está em andamento. Aguarde sua conclusão e tente novamente.',
    project_exists: 'Outro projeto já está cadastrado com esse diretório ou identidade.',
    source_conflict: 'Outra cópia deste repositório ainda está acessível. O cadastro existente foi preservado.',
    source_unavailable: 'Não foi possível acessar o projeto no host. Verifique o caminho, as permissões e o adaptador de arquivos.',
    catalog_metadata_conflict: 'Os metadados existentes precisam de recuperação. A identidade e a documentação foram preservadas.',
    management_unavailable: 'O serviço local de gestão está indisponível. Verifique a inicialização da aplicação.',
  };
  const communicationError = (errorCode && registrationErrors[errorCode]) || defaultCommunicationError;


  const acknowledge = useCallback(async (id: string) => {
    try {
      const response = await fetch('/api/catalog-management/acknowledge', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }), signal: AbortSignal.timeout(10000) });
      if (!response.ok) throw new Error('Unavailable');
    } catch { setError(true); }
  }, []);

  const receive = useCallback((next: Operation) => {
    setOperation(next);
    setTrackedProject(current => current && current.id === next.projectId ? { ...current, name: next.projectName ?? current.name, slug: next.projectSlug ?? current.slug } : projects.find(project => project.id === next.projectId) ?? (next.projectName && next.projectSlug ? { id: next.projectId, slug: next.projectSlug, name: next.projectName, description: '' } : current));
    if (next.removalReason === 'source_missing' && !next.notificationAcknowledged && !acknowledged.current.has(next.id)) setShowMissing(true);
    if (finished(next)) {
      if (next.removalReason === 'source_missing' && acknowledged.current.has(next.id) && !next.notificationAcknowledged) void acknowledge(next.id);
      if (!refreshed.current.has(next.id)) {
        refreshed.current.add(next.id);
        if (next.state === 'completed' && removing(next) && next.projectId) setRemoved(current => [...current, next.projectId!]);
        if (next.state === 'completed' && next.action === 'add' && next.projectId) setRemoved(current => current.filter(id => id !== next.projectId));
        router.refresh();
      }
    }
  }, [projects, router, acknowledge]);

  const modalOpen = !!selection || showMissing;
  useEffect(() => {
    if (helpOpen && helpDialog.current && !helpDialog.current.open) {
      helpDialog.current.showModal();
      helpDialog.current.querySelector('h2')?.focus();
      helpDialog.current.scrollTop = 0;
    }
    if (!helpOpen && helpDialog.current?.open) helpDialog.current.close();
  }, [helpOpen]);
  useEffect(() => {
    if (modalOpen && !dialog.current?.open) dialog.current?.showModal();
    if (!modalOpen && dialog.current?.open) dialog.current.close();
  }, [modalOpen]);

  useEffect(() => {
    if (!enabled) return;
    let disposed = false;
    const initialVersion = version.current;
    fetch('/api/catalog-management', { cache: 'no-store', signal: AbortSignal.timeout(10000) }).then(response => response.ok ? response.json() : null).then(data => {
      const current = data?.operation as Operation | undefined;
      if (!disposed && version.current === initialVersion && current && (!finished(current) || (current.removalReason === 'source_missing' && !current.notificationAcknowledged))) {
        receive(current);
        setSelection({ action: current.action ?? 'update' });
      }
    }).catch(() => {});
    return () => { disposed = true; };
    // Restore once per mounted catalog; a refreshed list must not reopen dismissed dialogs.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled]);

  const operationId = operation?.id;
  const terminal = operation ? finished(operation) : true;
  useEffect(() => {
    if (!operationId || terminal || submitting) return;
    let disposed = false;
    let timer: ReturnType<typeof setTimeout>;
    const currentVersion = version.current;
    const poll = async () => {
      try {
        const response = await fetch(`/api/catalog-management/${operationId}`, { cache: 'no-store', signal: AbortSignal.timeout(10000) });
        if (!response.ok) throw new Error('Unavailable');
        const data = await response.json();
        if (!data.operation || data.operation.id !== operationId) throw new Error('Unavailable');
        if (!disposed && version.current === currentVersion) {
          setError(false);
          receive(data.operation);
          if (finished(data.operation)) return;
        }
      } catch { if (!disposed && version.current === currentVersion) setError(true); }
      if (!disposed && version.current === currentVersion) timer = setTimeout(poll, 1000);
    };
    timer = setTimeout(poll, 300);
    return () => { disposed = true; clearTimeout(timer); };
  }, [operationId, terminal, submitting, receive]);

  function choose(next: Selection) {
    if (busy || submitGuard.current || showMissing) return;
    version.current += 1;
    setOperation(null);
    setTrackedProject(undefined);
    setError(false);
    setErrorCode(null);
    setSelection(next);
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selection || busy || operation || submitGuard.current) return;
    submitGuard.current = true;
    const currentVersion = ++version.current;
    const requestId = crypto.randomUUID().replaceAll('-', '');
    const form = new FormData(event.currentTarget);
    const body = selection.action === 'add' ? { ...Object.fromEntries(form), requestId } : { id: selection.project?.id, requestId };
    const pending: Operation = { id: requestId, action: selection.action, projectId: selection.project?.id, projectName: selection.project?.name, projectSlug: selection.project?.slug, state: 'requesting', phase: 'requesting' };
    setTrackedProject(selection.project);
    if (selection.action !== 'add') setOperation(pending);
    setSubmitting(true);
    setError(false);
    setErrorCode(null);
    let rejected = false;
    try {
      const response = await fetch(`/api/catalog-management/${selection.action}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: AbortSignal.timeout(selection.action === 'add' ? 160000 : 15000) });
      rejected = response.status >= 400 && response.status < 500;
      const data = await response.json();
      if (!response.ok) {
        if (version.current === currentVersion) setErrorCode(data.error ?? null);
        throw new Error('Rejected');
      }
      if (!data.operation?.id) throw new Error('Unavailable');
      if (version.current === currentVersion) receive({ ...pending, ...data.operation });
    } catch {
      if (version.current === currentVersion) {
        setError(true);
        if (rejected) setOperation(null);
      }
    } finally {
      submitGuard.current = false;
      setSubmitting(false);
    }
  }

  function close() {
    if (showMissing && operation) {
      acknowledged.current.add(operation.id);
      if (finished(operation)) void acknowledge(operation.id);
    }
    setShowMissing(false);
    setSelection(null);
  }

  const deleting = operation ? removing(operation) : selection?.action === 'remove';
  const statusMessage = error ? communicationError : operation && finished(operation) ? phases[operation.state] : deleting ? (en ? 'Deleting project...' : 'Excluindo projeto...') : (en ? 'Processing documentation...' : 'Processando documentação...');
  const project = trackedProject ?? selection?.project;
  const indicator = (busy || (operation && finished(operation) && operation.state !== 'completed')) && project ? { projectId: project.id, slug: project.slug, deleting: !!deleting, message: statusMessage, paused: error || !!(operation && finished(operation)) } : undefined;
  const visibleProjects = projects.filter(project => !project.id || !removed.includes(project.id));
  const add = en ? 'Add project' : 'Adicionar projeto';
  const title = showMissing ? (en ? 'Project not found' : 'Projeto não encontrado') : selection?.action === 'add' ? add : deleting ? (en ? 'Remove project' : 'Remover projeto') : (en ? 'Update documentation' : 'Atualizar documentação');
  const removalComplete = operation?.state === 'completed';
  const removalFailed = operation && finished(operation) && !removalComplete;
  return <>
    {visibleProjects.length ? <ProjectList projects={visibleProjects} language={language} page={page} operation={indicator} actionsDisabled={busy} onAction={enabled ? (action, project) => choose({ action, project }) : undefined}/> : <CatalogState kind="empty" language={language}/>}
    {indicator && !visibleProjects.some(item => item.id === indicator.projectId || item.slug === indicator.slug) && <div className="catalog-progress"><strong>{project?.name}</strong><OperationIndicator {...indicator}/></div>}
    {enabled && <div className="catalog-add"><button type="button" className="lang" disabled={busy} onClick={() => choose({ action: 'add' })}>{add}</button></div>}
    <dialog ref={dialog} className="catalog-dialog" aria-labelledby="catalog-dialog-title" onCancel={event => { event.preventDefault(); if (!submitting) close(); }} onClose={() => { setSelection(null); setShowMissing(false); }}>
      <form onSubmit={submit}>
        <h2 id="catalog-dialog-title">{title}</h2>
        {!showMissing && project && <p><strong>{project.name}</strong></p>}
        {showMissing ? <>
          <p>{en ? `The original directory for the project "${project?.name ?? operation?.projectName ?? ''}" could not be found.` : `Não foi possível localizar o diretório original do projeto "${project?.name ?? operation?.projectName ?? ''}".`}</p>
          <p>{removalComplete ? (en ? 'The project has been removed from Engineering Library, along with its local library documentation and catalog entry.' : 'O projeto foi removido da Engineering Library, juntamente com sua documentação local e seu registro no catálogo.') : removalFailed ? phases[operation!.state] : (en ? 'The project is being removed from Engineering Library, along with its local library documentation and catalog entry.' : 'O projeto está sendo removido da Engineering Library, juntamente com sua documentação local e seu registro no catálogo.')}</p>
        </> : <>
          {!operation && selection?.action === 'add' && <fieldset disabled={busy}>
            <div className="catalog-path-label">
              <label htmlFor="catalog-source-path">{en ? 'Relative project path' : 'Caminho relativo do projeto'}</label>
              <button ref={helpButton} type="button" className="catalog-path-help" aria-label={en ? 'How do relative paths work?' : 'Como funciona o caminho relativo?'} aria-haspopup="dialog" onClick={() => setHelpOpen(true)}>?</button>
            </div>
            <input id="catalog-source-path" name="sourcePath" aria-label={en ? 'Relative project path' : 'Caminho relativo do projeto'} required maxLength={4096} pattern={String.raw`(?!/|\\|[A-Za-z]:).+`} autoFocus placeholder={en ? '../example-project' : '../projeto-exemplo'}/>
          </fieldset>}
          {!operation && selection?.action === 'update' && <p>{en ? 'Do you want to update the documentation for this project?' : 'Você deseja atualizar a documentação deste projeto?'}</p>}
          {!operation && selection?.action === 'remove' && <p>{en ? 'Do you want to remove this project from Engineering Library? Its catalog entry and library documentation will be removed. The original source code will be preserved.' : 'Você deseja remover este projeto da Engineering Library? O registro do catálogo e sua documentação na biblioteca serão removidos. O código-fonte original será preservado.'}</p>}
        </>}
        {(busy || operation) && <div className="catalog-progress">{busy && selection?.action === 'add' ? <><p role="status">{en ? 'Registering project…' : 'Cadastrando projeto…'}</p><progress aria-label={en ? 'Project registration progress' : 'Progresso do cadastro'}/></> : busy ? <OperationIndicator deleting={!!deleting} message={statusMessage} paused={error}/> : <p role="status">{operation ? phases[operation.state] ?? statusMessage : ''}</p>}</div>}
        {operation?.error === 'source_unavailable' && <p role="alert">{en ? 'The source or its documentation mount is unavailable. Check the existing MakeDocs mounts.' : 'A origem ou seu mount documental está indisponível. Verifique os mounts existentes do MakeDocs.'}</p>}
        {error && <p role="alert">{communicationError}</p>}
        <div className="catalog-dialog-actions">
          {!operation && !showMissing && <button className="lang" type="submit" disabled={busy}>{selection?.action === 'add' ? add : selection?.action === 'remove' ? (en ? 'Yes, remove' : 'Sim, remover') : (en ? 'Yes, update' : 'Sim, atualizar')}</button>}
          <button className="lang" type="button" disabled={submitting && !showMissing} onClick={close}>{showMissing ? (en ? 'Understood' : 'Entendido') : operation ? (en ? 'Close' : 'Fechar') : (en ? 'Cancel' : 'Cancelar')}</button>
        </div>
      </form>
    </dialog>
    <dialog ref={helpDialog} className="catalog-dialog catalog-relative-help" aria-labelledby="catalog-relative-help-title" onKeyDown={event => { if (event.key === 'Tab') { event.preventDefault(); helpDialog.current?.querySelector('button')?.focus(); } }} onCancel={event => { event.preventDefault(); event.stopPropagation(); setHelpOpen(false); }} onClose={() => { setHelpOpen(false); helpButton.current?.focus(); }}>
      <h2 id="catalog-relative-help-title" tabIndex={-1}>{en ? 'How do relative paths work?' : 'Como funciona o caminho relativo?'}</h2>
      <p>{en ? 'A relative path describes how to reach another directory from a reference directory. Here, the reference is the Engineering Library repository root (engineering-library/).' : 'Um caminho relativo indica como chegar a outro diretório a partir de uma pasta de referência. Aqui, a referência é a raiz do repositório Engineering Library (engineering-library/).'}</p>
      <ul className="catalog-path-explanation">
        <li><code>./</code> {en ? 'represents the reference directory.' : 'representa a pasta de referência.'}</li>
        <li><code>../</code> {en ? 'moves up one directory level.' : 'sobe um nível na estrutura de diretórios.'}</li>
        <li><code>../../</code> {en ? 'moves up two directory levels.' : 'sobe dois níveis.'}</li>
        <li>{en ? 'The remaining path identifies the directories leading to the target project.' : 'O restante do caminho indica as pastas até chegar ao projeto desejado.'}</li>
      </ul>
      <figure className="catalog-directory-diagram">
        <figcaption>{en ? 'Example: start at engineering-library/ and follow the paths below.' : 'Exemplo: parta de engineering-library/ e siga os caminhos abaixo.'}</figcaption>
        <ul className="catalog-directory-tree">
          <li><span className="catalog-folder" aria-hidden="true"/>{en ? 'User/' : 'Usuário/'}
            <ul>
              <li><span className="catalog-folder" aria-hidden="true"/>{en ? 'Projects/' : 'Projetos/'}
                <ul>
                  <li className="catalog-directory-start"><span className="catalog-folder" aria-hidden="true"/><strong>engineering-library/</strong><small>{en ? 'Start · reference directory' : 'Início · pasta de referência'}</small></li>
                  <li><span className="catalog-folder" aria-hidden="true"/>{en ? 'example-project/' : 'projeto-exemplo/'}<small>{en ? '↑ 1 level → target' : '↑ 1 nível → destino'}<code>{en ? '../example-project' : '../projeto-exemplo'}</code></small></li>
                </ul>
              </li>
              {[
                ['Downloads', 'env-auditor'],
                ['Desktop', en ? 'another-project' : 'outro-projeto'],
                ['Pictures', en ? 'image-project' : 'projeto-imagem'],
              ].map(([folder, target]) => <li key={folder}><span className="catalog-folder" aria-hidden="true"/>{folder}/<ul><li><span className="catalog-folder" aria-hidden="true"/>{target}/<small>{en ? '↑ 2 levels → target' : '↑ 2 níveis → destino'}<code>../../{folder}/{target}</code></small></li></ul></li>)}
            </ul>
          </li>
        </ul>
      </figure>
      <p>{en ? 'The diagram is illustrative. Count levels from your Engineering Library repository. The target must be accessible through the application’s existing filesystem configuration and authorized source mounts.' : 'O diagrama é ilustrativo. Conte os níveis a partir do seu repositório Engineering Library. O destino precisa estar acessível pela configuração de arquivos e pelos mounts de origem já autorizados da aplicação.'}</p>
      <div className="catalog-dialog-actions"><button type="button" className="lang" onClick={() => setHelpOpen(false)}>{en ? 'Understood' : 'Entendido'}</button></div>
    </dialog>
  </>;
}
