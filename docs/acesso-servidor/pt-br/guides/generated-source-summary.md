# Resumo do código (rascunho gerado)

As explicações do modelo exigem revisão factual e bilíngue. Citações literais foram conferidas; este comando não executou o runtime. Este resumo limitado não substitui documentação humana.

Projeto: acesso-servidor. Geração: 1.9.2; modelo: llama3.2:3b; evidência SHA-256: eb875e4c8ae827720609020443065b0cb360facc2652b5572caeb1939b4e4282.

Cobertura: 1/5 arquivos candidatos; explicit; 4 omitidos.

A preparação usa declarações extraídas pelo chamador e trechos delimitados pelo layout quando suportados. São auxílio determinístico, não descobertas autônomas do modelo nem verificação de runtime.

## 1

O script verifica se o caminho do repositório coincide com o caminho esperado comparando o resultado do comando `git rev-parse --show-toplevel` com o caminho do repositório. Se não coincidirem, ele para com um erro de mensagem.

Fonte: `atualizar_codigo.sh:1`; SHA-256: `3260ca119c89ae7062501a2c4cde1b961c56083443b724345567714b95f731c1`.

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


