# helix — Edit operations

Temporary reviewed partial model excerpt. Important contracts remain undocumented. Not approved for publication; source quotes and full review evidence are preserved separately.

Source revision: `49986e6674e5658164a88f599ec8c822e62ad0db`.

## 1

The `Operation` enum supports three types of operations: `Retain`, `Delete`, and `Insert`. The `len_chars` method returns the number of characters affected by the operation.

Source: `helix-core/src/transaction.rs:7`; SHA-256: `9538319c6e595d808c61338b69036caac2d420eb07819ec2d964af43550cb4a6`.

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


