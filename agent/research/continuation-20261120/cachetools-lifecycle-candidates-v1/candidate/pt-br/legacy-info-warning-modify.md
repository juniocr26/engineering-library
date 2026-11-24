# O quarto booleano posicional legado continua sem aviso?

O `cached` atual reconhece o booleano na nova quarta posição como configuração legada de estatísticas, limpa seu valor de condição e emite `DeprecationWarning`. A observação própria com filtro explícito de avisos manteve as estatísticas; o booleano não se tornou sincronização por condição.
