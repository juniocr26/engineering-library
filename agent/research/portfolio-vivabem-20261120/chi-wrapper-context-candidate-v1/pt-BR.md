# Wrappers de resposta do Chi: capacidades e contabilização compartilhada

Candidato de desenvolvimento limitado à fonte, sem aprovação do proprietário. Revisão `9f8adb1aabaa8a91180a821111d3f8e668d1c0bf`, `middleware/wrap_writer.go` e `middleware/wrap_writer_test.go`. A fonte foi lida e analisada sintaticamente; o programa e os testes do Chi não foram executados. Este capítulo descreve a implementação escrita selecionada, sem abranger todo o comportamento do servidor.

## Seleção e arquitetura

`NewWrapResponseWriter` começa com `basicWriter{ResponseWriter: w}` e verifica `http.Flusher`. Quando `protoMajor == 2`, suporte a flush e a `http.Pusher` seleciona `http2FancyWriter`. Outros valores de protocolo entram no ramo que verifica `http.Hijacker` e `io.ReaderFrom`: as três capacidades selecionam `httpFancyWriter`; flush com hijacking seleciona `flushHijackWriter`; somente hijacking seleciona `hijackWriter`. A alternativa final seleciona `flushWriter` quando há flush, ou o wrapper básico caso contrário. Essa é a seleção literal, não uma prova de validade de todo valor de protocolo de rede. [S1]

Cada wrapper selecionado incorpora o estado básico. `WrapResponseWriter` declara operações de status, bytes, tee, unwrap e descarte além de `http.ResponseWriter`; não declara `ReadFrom`. Portanto, o chamador não deve concluir que todo wrapper retornado suporta `io.ReaderFrom`. O comentário acima de `http2FancyWriter` menciona essa interface, mas o arquivo selecionado declara seus métodos `Flush` e `Push` e nenhum método `ReadFrom` para esse receptor. Não se afirma ausência em todo o repositório nem uma prova completa de conjunto de métodos ou verificação de tipos do Go. [S1,S2,S6]

## Estado e contratos de escrita

`Status()` retorna `b.code`; `BytesWritten()` retorna `b.bytes`. São contadores do wrapper, não observações independentes de entrega ao cliente. No modo de descarte, a implementação ainda contabiliza as escritas consumidas, como espera explicitamente o teste escrito. `Tee(w)` substitui o único destino tee; `Unwrap()` retorna o writer original; `Discard()` define a flag de descarte. O comentário da interface proíbe modificar o writer tee simultaneamente às escritas; nenhuma garantia de sincronização é demonstrada aqui. [S2,S4,T2]

`WriteHeader` trata códigos de 100 a 199, exceto `http.StatusSwitchingProtocols`, em um ramo informativo: delega somente sem descarte e não atribui ali os campos de estado final. Nos demais casos, somente a primeira chamada enquanto `!b.wroteHeader` atribui código e flag, delegando apenas sem descarte. `maybeWriteHeader()` chama `WriteHeader(http.StatusOK)` quando a flag é falsa. `flush()` invoca esse helper antes de delegar condicionalmente `Flush`; o descarte suprime o flush subjacente. [S3]

`Write` começa chamando esse helper. No modo normal escreve na resposta subjacente e depois envia somente `buf[:n]` ao tee, se definido. O erro da escrita subjacente tem preferência: o erro do tee só o substitui quando o primeiro é nil. No descarte, o tee recebe toda a entrada se existir; caso contrário, a chamada usa `io.Discard.Write`. O contador básico aumenta pelo `n` retornado. Esses ramos explicam por que um comentário de interface sobre bytes enviados não justifica uma afirmação universal de entrega ao cliente. [S3,T1,T2]

## ReadFrom: delegação e revisão

Se houver tee ou descarte, `httpFancyWriter.ReadFrom` usa `io.Copy(&f.basicWriter, r)` e retorna imediatamente. O caminho de `Write` básico já atualiza seu contador, portanto esse ramo não soma novamente a contagem retornada. Isso preserva o encaminhamento escrito de tee/descarte, em vez de contorná-lo pelo writer original. O comportamento efetivo de `io.Copy` pertence ao runtime e às implementações de reader/writer; não foi executado aqui. [S5,T3,T4]

Caso contrário, o método faz uma asserção do writer original como `io.ReaderFrom`, chama `rf.ReadFrom(r)` e registra status implícito de sucesso somente sob `n > 0 && !f.basicWriter.wroteHeader`. Depois soma `int(n)` ao contador de bytes e retorna a mesma contagem e erro. O código selecionado não exige `err == nil` para essas atualizações contábeis. Não chama `WriteHeader` do wrapper nesse ramo direto. A verificação de capacidades da fábrica explica o caminho pretendido da asserção; construção manual arbitrária ainda exige um writer subjacente compatível e não tem segurança garantida. [S1,S5]

A revisão anterior selecionada chamava `f.basicWriter.maybeWriteHeader()` antes de `rf.ReadFrom(r)`. O ramo direto atual atualiza o estado registrado depois do retorno do delegado, condicionado a contagem positiva e cabeçalho ainda não registrado. Essa mudança de ordem/condição é relevante à documentação, sem provar cabeçalhos efetivos do transporte ou desempenho geral. A estrutura sem dupla contagem do fallback é outro contrato da fonte atual, não atribuído àquela alteração histórica selecionada de uma linha. [H1,S5]

## Exemplo e testes escritos

Um fragmento moldado pela fonte recebe um response writer existente; não inicia servidor:

```go
func observe(w http.ResponseWriter) int {
    wrapped := middleware.NewWrapResponseWriter(w, 1)
    wrapped.Discard()
    return wrapped.BytesWritten()
}
```

O arquivo que contiver o fragmento precisa de `net/http` e do pacote `middleware` do módulo. Ele demonstra somente construção do wrapper e uso do acessor; revisão sintática não equivale a compilação nem resultado em execução. Nenhum comando de preparação ou testes foi executado. [S1,S4]

Os testes escritos cobrem status e supressão de flush, escrita comum com tee, descarte com e sem tee, contagem no caminho de `ReadFrom` com tee e supressão do corpo original no caminho de `ReadFrom` com descarte. Os últimos constroem wrappers manualmente e verificam a contagem consumida; não estabelecem toda a matriz de capacidades da fábrica. O helper `readerFromRecorder.ReadFrom` copia para o corpo do recorder. São asserções documentadas, não resultados de testes aprovados. [T1,T2,T3,T4,T5]

## FAQ

**Todo wrapper suporta `ReadFrom`?** Não existe esse contrato universal em `WrapResponseWriter`; a seleção depende de capacidades. O comentário selecionado sobre HTTP2 é evidência insuficiente. [S1,S2,S6]

**Os bytes do tee são contados duas vezes?** O fallback selecionado retorna o resultado de `io.Copy` sem segundo incremento; as escritas básicas fazem a própria contabilização. O teste de regressão escrito espera uma contagem igual ao tamanho da entrada. [S3,S5,T3]

**Descarte significa contador zerado?** Não. O caminho básico contabiliza escritas mesmo quando contorna o writer original, e os testes escritos de descarte esperam bytes consumidos. [S3,T2,T4]

**O `ReadFrom` direto sempre confirma um cabeçalho do wrapper antes da leitura?** Não. O método atual selecionado registra o estado depois da chamada delegada somente sob sua condição de contagem positiva/cabeçalho não registrado. Isso não garante comportamento em execução do writer original. [S5,H1]

## Evidências e limites

S1: fonte, linhas 15–44. S2: 46–81. S3: 83–128. S4: 130–148. S5: 211–229. S6: 203–209 e 231–248. T1: testes, linhas 116–134. T2: 136–174. T3: 181–198. T4: 204–220. T5: 21–114. H1: mesmo caminho da fonte em `04f7f55a7b5ddb2ecd79a8d813b2256c1113b8a9`, `httpFancyWriter.ReadFrom`, congelado separadamente. Snapshots e seleções sintáticas nativas foram preservados junto deste candidato. Sem dados privados, alterações externas, execução do projeto, aprovação do proprietário ou promoção a gold de treinamento.
