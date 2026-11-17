# Resumo do código (rascunho gerado)

As explicações do modelo exigem revisão factual e bilíngue. Citações literais foram conferidas; este comando não executou o runtime. Este resumo limitado não substitui documentação humana.

Projeto: payment-reconciliation-lab. Geração: 1.9.2; modelo: llama3.2:3b; evidência SHA-256: e831b5a6acca4d6729cf8634fdba04c3aff20e7599f424610093ec5b40d68419.

Cobertura: 1/22 arquivos candidatos; explicit; 21 omitidos.

A preparação usa declarações extraídas pelo chamador e trechos delimitados pelo layout quando suportados. São auxílio determinístico, não descobertas autônomas do modelo nem verificação de runtime.

## 1

A estrutura do registro ProductSummary em Java suporta um produto com um identificador único (UUID), slug, nome, descrição, preço, categoria, caminho do arquivo de imagem e informações de disponibilidade. Essa estrutura de registro é usada para resumir detalhes do produto na aplicação.

Fonte: `backend/src/main/java/com/aurorabakery/catalog/application/ProductSummary.java:1`; SHA-256: `3f9b9317a2d1300411d7661a1aa330537355cde819f78999091d30c7aab6fd19`.

    package com.aurorabakery.catalog.application;
    import com.aurorabakery.catalog.domain.Availability;
    import java.math.BigDecimal;
    import java.util.UUID;
    public record ProductSummary(UUID id,String slug,String name,String description,BigDecimal price,String category,String imagePath,boolean featured,Availability availability,boolean purchasable) {}


