# A fachada selecionada usa a mesma estratégia de sincronização nos dois recortes?

O `func._cache` mais recente fornece `Condition()`. Com o resultado próprio que pôde ser armazenado, uma chamada aguardando a mesma chave reutilizou o primeiro resultado e ocorreu uma computação; a fachada anterior computou duas vezes. Isso não estabelece execução global exatamente uma vez nem desempenho.
