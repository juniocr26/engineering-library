package owned
type Base struct{}
func (*Base) Value() int { return 7 }
func Read(b Base) int { return b.Value() }
