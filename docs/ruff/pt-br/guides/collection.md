# ruff

Rascunho de avaliação montado com passes locais independentes e limitados ao código. As explicações exigem revisão factual e bilíngue. Os arquivos selecionados não comprovam documentação completa do projeto.

Revisão: `0222c19dd8e0c9a927f2e47bf3774a108431da25`.

## Sumário

- [Resultados da CLI](#resultados-da-cli)
- [Seleção de entrada](#seleção-de-entrada)
- [Verificação e limitações técnicas](#verificação-e-limitações-técnicas)

<!-- reading-section: project-section-exit-status -->

## Resultados da CLI

### 1

A enum ExitStatus é usado para representar o resultado do linting, com Sucesso indicando que não há erros, Falha indicando um ou mais erros, e Erro indicando uma falha de linting. O trait From é implementado para converter ExitStatus para ExitCode, mapeando Sucesso para 0, Falha para 1, e Erro para 2.

Fonte: `crates/ruff/src/lib.rs:37`; SHA-256: `0ef764772b4d62ea35232b09f2fe7a578dc5211451bf59fabd4e653251c276c6`.

    #[derive(Copy, Clone)]
    pub enum ExitStatus {
        /// Linting was successful and there were no linting errors.
        Success,
        /// Linting was successful but there were linting errors.
        Failure,
        /// Linting failed.
        Error,
    }
    
    impl From<ExitStatus> for ExitCode {
        fn from(status: ExitStatus) -> Self {
            match status {
                ExitStatus::Success => ExitCode::from(0),
                ExitStatus::Failure => ExitCode::from(1),
                ExitStatus::Error => ExitCode::from(2),
            }
        }
    }




<!-- reading-section: project-section-stdin -->

## Seleção de entrada

### 1

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




<!-- reading-section: project-verification -->

## Verificação e limitações técnicas

As evidências de runtime/build estão registradas separadamente no relatório da campanha. Este comando não executa o código descoberto nem certifica comportamento de GUI/GPU/dispositivos.
