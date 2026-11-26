# Source summary (generated draft)

Model explanations require factual and bilingual review. Exact quotes were checked; runtime was not executed by this command. This bounded summary does not replace human documentation.

Project: acesso-servidor. Generation: 1.9.2; model: llama3.2:3b; evidence SHA-256: eb875e4c8ae827720609020443065b0cb360facc2652b5572caeb1939b4e4282.

Coverage: 1/5 candidate files; explicit; 4 omitted.

Evidence preparation uses caller-extracted declarations and source-layout excerpts where supported. These are deterministic assistance, not autonomous model findings or runtime verification.

## 1

The script checks if the repository path matches the expected path by comparing the output of `git rev-parse --show-toplevel` with the repository path. If they do not match, it stops with an error message.

Source: `atualizar_codigo.sh:1`; SHA-256: `3260ca119c89ae7062501a2c4cde1b961c56083443b724345567714b95f731c1`.

    #!/usr/bin/env bash
    # Run separately before deployment; never replace a running deploy script.
    set -euo pipefail
    SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
    exec "${PYTHON_BIN:-python3}" - "$SCRIPT_DIR" <<'PY'
    import os
    from pathlib import Path
    import subprocess
    import sys
    
    repo = Path(sys.argv[1])
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])
    def stop(message):
        print('ERRO: ' + message, file=sys.stderr)
        sys.exit(1)
    try:
        if Path(os.fsdecode(git('rev-parse', '--show-toplevel')).strip()).resolve() != repo:
            stop('Raiz do repositório inesperada.')
        remote = os.fsdecode(git('remote', 'get-url', 'origin')).strip().rstrip('/')
        if remote.rsplit('/', 1)[-1].removesuffix('.git') != 'acesso-servidor':
            stop('origin não identifica acesso-servidor.')
        for name in ('atualizar_projetos.sh', 'deployment_guard.py'):
            git('ls-files', '--error-unmatch', '--', name)
        if git('diff', '--cached', '--name-only', '-z'):
            stop('Alterações staged; revise manualmente.')
        deletions = []
        for record in git('status', '--porcelain=v1', '-z', '--untracked-files=all').split(b'\0'):
            if not record:
                continue
            state, name = record[:2], os.fsdecode(record[3:])
            if state == b'??':


