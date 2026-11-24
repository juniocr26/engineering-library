package owned
type Base struct{}
func (Base) Value() int { return 7 }
type Child struct{ Base; Value int }
func Read(c Child) int { return c.Value() }
