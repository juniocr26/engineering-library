package owned
type A struct{}
func(A) Value()int{return 1}
type B struct{}
func(B) Value()int{return 2}
type Child struct{A;B}
func Read(c Child)int{return c.Value()}
