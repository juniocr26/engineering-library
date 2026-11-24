package main

import "github.com/twpayne/go-geom"

func main() {
    p := geom.NewPointFlat(geom.XY, []float64{1, 2})
    q := p.Clone()
    if _, err := q.SetCoords([]float64{3, 4}); err != nil {
        panic(err)
    }
}
