# Contabilização de ReadFrom depois da revisão fixada

Este candidato isolado de manutenção descreve `middleware.httpFancyWriter.ReadFrom` de `go-chi/chi` em `9f8adb1aabaa8a91180a821111d3f8e668d1c0bf`. Sua revisão anterior é `04f7f55a7b5ddb2ecd79a8d813b2256c1113b8a9`. A revisão altera o ramo sem tee e sem descarte; esta é uma descrição do código, não um teste de runtime aprovado.

Quando `f.basicWriter.tee != nil || f.basicWriter.discard`, o método continua chamando `io.Copy(&f.basicWriter, r)` e retorna imediatamente seu par de resultados. Esse ramo não alcança o caminho direto de `ReaderFrom` subsequente. Evidência: `middleware/wrap_writer.go:211–220` nas duas revisões fixadas.

Antes, o caminho direto fazia a asserção `ResponseWriter.(io.ReaderFrom)`, chamava `f.basicWriter.maybeWriteHeader()` e depois chamava `rf.ReadFrom(r)`. Acumulava `int(n)` e retornava `n, err`. Evidência: antigo `middleware/wrap_writer.go:221–225`.

O caminho direto revisado chama `rf.ReadFrom(r)` primeiro. Se essa chamada retorna normalmente, a condição escrita `n > 0 && !f.basicWriter.wroteHeader` atribui condicionalmente `http.StatusOK` ao campo `code` do wrapper e define `wroteHeader = true`. A condição não testa `err == nil`. Em seguida, soma `int(n)` a `bytes` e retorna `n, err`. Evidência: novo `middleware/wrap_writer.go:221–228`.

A chamada removida de `maybeWriteHeader()` antes alcançava `WriteHeader(http.StatusOK)` quando `wroteHeader` era falso. Já o novo bloco contém atribuições aos campos do wrapper, em vez de uma chamada direta a `WriteHeader`. `Status()` retorna `code`, e `BytesWritten()` retorna `bytes`. Evidência: novo `middleware/wrap_writer.go:117–120,130–135` e antigo `:117–120`.

## FAQ

**Isso significa que todo ReadFrom informa StatusOK?** Não. O bloco revisado de contabilização exige tanto `n > 0` quanto `wroteHeader` falso depois que o delegado retorna. O estado existente do wrapper e o ramo inicial importam.

**Um n positivo prova que o erro é nil?** Não. A condição mostrada não examina `err`; o par de resultados retornado é preservado.

**A revisão executa o mesmo caminho para Tee ou Discard?** Não. O ramo anterior usa `io.Copy` e retorna antecipadamente. Este candidato não certifica o comportamento de runtime de `io.Copy`, do writer ou da rede.

**O que foi efetivamente verificado?** Snapshots exatos obtidos do Git somente para leitura, o diff real da revisão, a declaração do receiver pelo parser de sintaxe Go já incluído e a ordem descrita no código. Não foi executada suíte externa de testes, verificação de tipos Go, servidor HTTP ou escrita na rede.

Este é um candidato de manutenção do código revisado manualmente, não aprovação do proprietário, gold de treinamento, verificador geral ou resultado de holdout independente.
