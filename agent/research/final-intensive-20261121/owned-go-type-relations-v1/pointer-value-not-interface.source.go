package owned
type Base struct{}
func (*Base) Value() int { return 7 }
type Reader interface { Value() int }
var _ Reader = Base{}
