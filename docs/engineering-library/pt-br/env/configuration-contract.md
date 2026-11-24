# Contrato de configuração sem valores

Revisado em 04/11/2026 por declarações do código, sem abrir dotenv, credenciais, dados runtime ou arquivos de assinatura. Exigências por funcionalidade diferem de requisitos de boot. Referência env() sozinha não torna uma variável globalmente obrigatória.

| Chave / entrada | Contrato |
| --- | --- |
| `POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, SECRET_KEY_BASE` | Exigidos pelo Compose existente; valores privados da instalação |
| `FRONTEND_PORT, BACKEND_PORT, POSTGRES_PORT` | Bindings opcionais do host: defaults 3099/3098/5499 em loopback |
| `LOCAL_UID, LOCAL_GID` | Identidade opcional de desenvolvimento default 1000:1000; não implica reparo recursivo |
| `CATALOG_ROOT, DOCUMENTATION_ROOT` | Montagens catálogo/leitor; Compose fornece localizações nos containers |


Use configuração/guia de ambiente/runbook existentes para alterações operacionais. Nunca cole valores privados no catálogo, copie ambiente efetivo ou execute atualizador mutante como verificação documental. Nenhum arquivo de ambiente, variável, esquema ou serviço foi alterado.
