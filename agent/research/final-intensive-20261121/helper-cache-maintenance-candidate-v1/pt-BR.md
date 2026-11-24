# Validação de cache do helper delimitado: candidato de manutenção

Nota de alteração somente para pesquisa em engineering-library, de b586e484a56ef7e868c7257b2ea11ad9f71b606b para 7dbc3b696ddafb6a302ae47ea412e85b587bc308. Público: operadores da API opcional de obtenção de fonte. Descreve o fluxo de controle estático selecionado, sem cobrir toda a arquitetura do helper ou comportamento observado em runtime.

R01: A versão selecionada do helper é 0.1.5.

Source: agent/tools/documentation_retrieval.py:[21, 21] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R02: A validação de unidades Python reconstrói o callable léxico selecionado e compara as unidades de evidência canônicas.

Source: agent/tools/documentation_retrieval.py:[98, 102] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R03: A validação de unidades Go chama a extração e compara a unidade canônica resultante.

Source: agent/tools/documentation_retrieval.py:[109, 113] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R04: Um resultado FOUND em cache chama validate_unit durante a validação do resultado em cache.

Source: agent/tools/documentation_retrieval.py:[145, 148] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R05: O caminho de extração nova também chama validate_unit e captura subprocess.SubprocessError em seu tratador interno de extração.

Source: agent/tools/documentation_retrieval.py:[425, 439] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R06: O subprocesso selecionado de extração Go usa timeout=20; um timeout não é obtenção bem-sucedida da fonte.

Source: agent/tools/documentation_retrieval.py:[267, 269] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R07: O caminho de duplicata chama validate_cached fora do tratador interno da extração nova.

Source: agent/tools/documentation_retrieval.py:[399, 413] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

R08: O wrapper JobBoundRetrieval mostrado retorna UNKNOWN_COMPLETION quando helper.request lança uma Exception.

Source: agent/tools/documentation_job_budget.py:[306, 310] @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308

A versão anterior da fonte do helper era 0.1.3; o guia existente ainda identifica essa versão e descreve verificações de citações físicas. A revisão da fonte acrescenta reconstrução e comparação de toda a unidade léxica. O guia existente portanto precisa de MODIFY dentro deste escopo declarado.

A tupla externa de exceções do helper não inclui subprocess.SubprocessError, enquanto a tupla interna da extração nova inclui. No caminho de duplicata mostrado, uma exceção do subprocesso Go pode escapar para o wrapper do job. Não prometa que toda revalidação em cache retorna um status normal ou que um subprocesso que falhou obteve evidência válida. O chamador deve preservar a incerteza e a evidência do job reservado. Nenhum replay automático se justifica aqui.

Nenhuma fonte externa, requisição ao helper, falha de subprocesso ou teste de aplicação foi executado para este candidato. Os recibos históricos do defeito ficam separados. Evidência léxica não é vínculo em runtime, semântica da fonte, permissão de publicação ou Gold de treinamento. Exemplos e comandos operacionais estão fora do escopo desta nota delimitada. Este candidato foi escrito manualmente; não se alega melhoria neural.
