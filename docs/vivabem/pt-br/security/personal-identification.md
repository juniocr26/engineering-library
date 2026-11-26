# Identidade por papel e minimização de dados pessoais

Revisão de fonte privada autorizada em 12/11/2026. Esta explicação pública generaliza os padrões observados; não reproduz código proprietário, contratos internos ou registros de produção. [Índice](../index.md).

## Conta, perfil e participação são identidades relacionadas

Uma conta autentica a pessoa; um perfil descreve um papel; uma participação define o papel naquela consulta. Um profissional que compra uma consulta atua como paciente nesse atendimento. Resolver destinatário, nome e imagem pela flag global da conta produz resultados incorretos quando ambos os papéis existem. A resolução deve partir dos participantes do atendimento e depois escolher o perfil correspondente.

No comportamento inspecionado, o destinatário paciente vê a identificação profissional da contraparte, incluindo CRP quando disponível. O profissional vê a identificação do paciente, sem acrescentar o CRP que esse paciente possa possuir. Falta de região ou número do registro tem fallback textual; ausência de imagem contextual pode recorrer à imagem global e depois a avatar padrão. Fallback preserva usabilidade, mas pode perder especificidade do papel. [Notificações](../architecture/contextual-notifications.md).

## CPF e CNPJ têm contratos diferentes

CPF identifica pessoa física e é obrigatório nos cadastros de paciente e profissional inspecionados. A entrada é normalizada para dígitos, verifica tamanho, repetição e os dois dígitos verificadores; a unicidade é declarada por tabela de perfil. Isso detecta erros de formato, não prova titularidade, existência oficial ou unicidade entre todos os papéis. Máscara de exibição não é mecanismo de proteção.

O fluxo profissional atual também possui CNPJ opcional, com normalização, verificação numérica e persistência/edição. Omissão em edição preserva o valor; entrada vazia pode removê-lo após normalização. CNPJ não substitui CPF e a implementação observada não demonstra validação fiscal externa ou suporte a formatos alfanuméricos. Não extrapolar uma regra local para obrigações legais ou tributárias.

## Exclusão da mensagem não é exclusão da API

Os produtores de notificações de consulta revisados usam nomes e identificação profissional, sem CPF nas mensagens. A projeção persistida do sino não inclui campo CPF. Isso reduz exposição entre canais, mas não cria um redator universal: strings arbitrárias fornecidas ao publicador podem conter dados pessoais. A origem da mensagem continua responsável pelo conteúdo.

Leituras autenticadas da aplicação ainda podem transportar documentos pessoais para telas e ações autorizadas. Não concluir que todo CPF foi removido das APIs. Tampouco declarar criptografia de campo ou ocultação automática de serialização quando os modelos não demonstram esses controles. Autenticação, autorização por objeto e minimização por campo precisam ser avaliadas separadamente.

Exemplo sintético: a mensagem “Sua consulta com a profissional foi confirmada” não precisa do documento fiscal de nenhuma parte. O detalhe autenticado pode exigir mais contexto, mas cada campo deve ter finalidade e autorização verificáveis. Não usar identificadores pessoais em chaves de cache, logs, tags de push ou exemplos públicos.

## Superfícies e trade-offs

Foto acessível por URL pública não é protegida só por possuir nome imprevisível. Push pode aparecer fora da sessão autenticada; até nome e vínculo de atendimento merecem revisão de necessidade. Exportação, backup e acesso administrativo também são superfícies de dados pessoais. TTL de notificações não define retenção dos perfis persistentes.

A arquitetura separa recuperação técnica e transição de negócio para evitar repetir operações pessoais/financeiras ao reenviar alertas. Ainda assim, proteção real depende dos privilégios efetivos, do escopo da consulta e de controles por item. Uma ação de leitura/marcação deve verificar associação do item ao usuário, não apenas existência de um identificador.

## Evidência e limites

A inspeção encontrou testes existentes para mensagens sem CPF, identificação profissional e fotos por papel, além de atomicidade de cadastro. São evidências de cenários definidos, não auditoria completa das APIs ou certificação de privacidade. Nenhum teste de aplicação ou consulta a dados pessoais foi executado nesta atualização.

Para futuras verificações, usar dados sintéticos, revisar projeções de resposta e testar autorização entre contas em ambiente isolado autorizado. A documentação não comprova conformidade legal, anonimização, criptografia em repouso ou validação de dispositivos de produção. Detalhes de implementação, achados específicos e procedimentos operacionais ficam na documentação interna.
