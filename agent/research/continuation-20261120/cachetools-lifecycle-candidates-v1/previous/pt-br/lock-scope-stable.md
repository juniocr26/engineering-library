# Mover o auxiliar exige mudar toda afirmação sobre escopo do lock?

Em uma falta no cache, o wrapper selecionado de memoização apenas com lock chama a função do usuário fora do lock do cache. O caso próprio de duas threads computou duas vezes e retornou aos dois chamadores o valor que venceu no cache.
