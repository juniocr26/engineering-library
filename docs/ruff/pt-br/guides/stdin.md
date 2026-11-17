# Ruff — Seleção de entrada

As explicações do modelo exigem revisão factual e bilíngue. Citações literais foram conferidas; este comando não executou o runtime. Este resumo limitado não substitui documentação humana.

Projeto: ruff. Geração: 1.9.12; modelo: llama3.2:3b; evidência SHA-256: fc2a1ddf4d25ac96af48d7677a7eb041fd6c279e7f33fd3fbf4ec2db08c0b33f.

Cobertura: 1/1 arquivos candidatos; explicit project section; counts apply only to staged files, not whole repository coverage; 0 omitidos.

Escopo explícito de unidades nos arquivos abaixo; o conteúdo não selecionado desses arquivos não foi enviado:

    {}

Unidades selecionadas: 0; unidades citadas: 0.

A preparação usa declarações extraídas pelo chamador e trechos delimitados pelo layout quando suportados. São auxílio determinístico, não descobertas autônomas do modelo nem verificação de runtime.

## 1

A função `is_stdin` suporta a condição de que se o usuário forneceu um nome de arquivo `--stdin-filename`, o programa lê sempre do padrão de entrada.

Fonte: `crates/ruff/src/lib.rs:96`; SHA-256: `0ef764772b4d62ea35232b09f2fe7a578dc5211451bf59fabd4e653251c276c6`.

    fn is_stdin(files: &[PathBuf], stdin_filename: Option<&Path>) -> bool {
        // If the user provided a `--stdin-filename`, always read from standard input.
        if stdin_filename.is_some() {
            if let Some(file) = files.iter().find(|file| file.as_path() != Path::new("-")) {
                warn_user_once!(
                    "Ignoring file {} in favor of standard input.",
                    file.display()
                );
            }
            return true;
        }
    
        let [file] = files else {
            return false;
        };
        // If the user provided exactly `-`, read from standard input.
        file == Path::new("-")
    }
    
    /// Returns the default set of files if none are provided, otherwise returns provided files.
    fn resolve_default_files(files: Vec<PathBuf>, is_stdin: bool) -> Vec<PathBuf> {
        if files.is_empty() {
            if is_stdin {
                vec![Path::new("-").to_path_buf()]
            } else {
                vec![Path::new(".").to_path_buf()]
            }
        } else {
            files
        }
    }


