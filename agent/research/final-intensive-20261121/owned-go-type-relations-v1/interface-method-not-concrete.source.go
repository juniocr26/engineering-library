package owned
type Reader interface { Value() int }
func Read(r Reader) int { return r.Value() }
