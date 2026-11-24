package owned
type Base struct{}
func (Base) Value() int { return 7 }
var methodExpression = Base.Value
var boundMethod = Base{}.Value
