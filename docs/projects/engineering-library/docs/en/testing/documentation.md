# Validation and limits

[Existing documentation validator](../../../../../en/guides/documentation-validator.md).

The current scanner covers READMEs and docs/en and docs/pt-BR; it does not traverse the new docs/projects. Collection validation must also check links, path parity and reachability from project indexes. Existing Rails tests check /up, password nondisclosure and SELECT 1; definitions were inspected without execution. Frontend lint, typecheck and build do not prove implemented catalog navigation.
