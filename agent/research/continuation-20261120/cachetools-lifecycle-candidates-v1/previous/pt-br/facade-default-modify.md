# A fachada selecionada usa a mesma estratégia de sincronização nos dois recortes?

O `func._cache` selecionado fornece `RLock()` e as chamadas próprias com a mesma chave computaram duas vezes.
