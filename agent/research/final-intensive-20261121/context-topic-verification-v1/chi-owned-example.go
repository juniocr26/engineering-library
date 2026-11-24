package ownedexample
import ("net/http"; middleware "github.com/go-chi/chi/v5/middleware")
func observe(w http.ResponseWriter) int {
    wrapped := middleware.NewWrapResponseWriter(w, 1)
    wrapped.Discard()
    return wrapped.BytesWritten()
}
