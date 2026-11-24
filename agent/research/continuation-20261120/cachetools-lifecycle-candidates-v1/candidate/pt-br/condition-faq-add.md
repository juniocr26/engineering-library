# O que o novo argumento `condition` disponível coordena?

Com uma condição padrão e um cache que armazena o resultado, o wrapper selecionado acompanha chaves pendentes e permite que uma chamada aguardando a mesma chave reutilize o resultado armazenado. A computação própria de outra chave avançou separadamente. Isso é coordenação limitada dentro de um processo, não uma garantia distribuída de execução exatamente uma vez.
