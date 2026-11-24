package owned

func Selected(value int) int {
	return value + 1
}

func Other(value int) int {
	return value + 9
}

type One struct{}
type Two struct{}

func (One) Selected(value int) int {
	return value + 2
}

func (Two) Selected(value int) int {
	return value + 7
}
