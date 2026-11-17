# redis — Entradas de compilação

Trecho parcial temporário do modelo, revisado. Contratos importantes continuam sem documentação. Sem aprovação de publicação; citações do código e evidências completas da revisão ficam preservadas separadamente.

Revisão de origem: `1a9eb051aa243f9d0e5a8a8afa6c4801bf52a9fb`.

## 1

O arquivo Makefile explicitamente exporta a variável MAKE para garantir que as receitas de shell possam lê-la como $MAKE e usarem o mesmo binário de make que o usuário invocou. Isso evita problemas potenciais com o lookup de caminho da variável make no shell não interativo de receitas.

Fonte: `Makefile:1`; SHA-256: `5998d578a530e0ba58f0877c1f7262ca3a9c18e46c72f0dfec6b78f8e5ab2b48`.

    # Top level makefile, the real stuff is at ./src/Makefile and in ./modules/Makefile
    
    # Explicitly export $(MAKE) so recipe shells (scripts/build.sh, deploy.sh, ...)
    # can read it as $MAKE and use the same make binary the user invoked. GNU make
    # only auto-propagates MAKE to recursive `$(MAKE) -C ...` sub-makes — recipes
    # that are shell scripts get an EMPTY $MAKE env var by default. Without this,
    # `MAKE_BIN="${MAKE:-make}"` in scripts falls back to PATH-lookup of `make`,
    # which can resolve to Apple's stock /usr/bin/make 3.81 in non-interactive
    # recipe shells (different PATH ordering than the user's interactive shell).
    export MAKE
    
    .DEFAULT_GOAL := build
    
    # Used only by .DEFAULT: below, for goals with no explicit rule in
    # this Makefile (e.g. `make distclean`, `make 32bit`) — those still recurse
    # into src/ only, matching upstream Redis. Modules are never part of this;
    # `make` / `make build` route through scripts/build.sh instead,
    # which decides per-module inclusion from what's actually cloned under
    # modules/*/src, not from a build flag.
    SUBDIRS = src
    
    # Manifest parser (modules.yaml → AVAILABLE_MODULES + helpers) shared with
    # per-module builds via modules/common.mk. The `sync-redis-conf` target lives
    # in this top-level Makefile (not in manifest.mk) so per-module builds —
    # which include common.mk → manifest.mk — don't see it as their default goal.
    include modules/manifest.mk
    
    # ----------------------------------------------------------------------------
    # Positional-arg capture for goals that take a list of module/test names.
    #


