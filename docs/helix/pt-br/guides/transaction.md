# helix — Operações de edição

Trecho parcial temporário do modelo, revisado. Contratos importantes continuam sem documentação. Sem aprovação de publicação; citações do código e evidências completas da revisão ficam preservadas separadamente.

Revisão de origem: `49986e6674e5658164a88f599ec8c822e62ad0db`.

## 1

A estrutura de operações suporta três tipos de operações: `Retain`, `Delete` e `Insert`. A função `len_chars` retorna o número de caracteres afetados pela operação.

Fonte: `helix-core/src/transaction.rs:7`; SHA-256: `9538319c6e595d808c61338b69036caac2d420eb07819ec2d964af43550cb4a6`.

    /// (from, to, replacement)
    pub type Change = (usize, usize, Option<Tendril>);
    pub type Deletion = (usize, usize);
    
    // TODO: pub(crate)
    #[derive(Debug, Clone, PartialEq, Eq)]
    pub enum Operation {
        /// Move cursor by n characters.
        Retain(usize),
        /// Delete n characters.
        Delete(usize),
        /// Insert text at position.
        Insert(Tendril),
    }
    
    impl Operation {
        /// The number of characters affected by the operation.
        pub fn len_chars(&self) -> usize {
            match self {
                Self::Retain(n) | Self::Delete(n) => *n,
                Self::Insert(s) => s.chars().count(),
            }
        }
    }


