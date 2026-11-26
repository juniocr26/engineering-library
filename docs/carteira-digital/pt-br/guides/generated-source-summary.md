# Resumo do código (rascunho gerado)

As explicações do modelo exigem revisão factual e bilíngue. Citações literais foram conferidas; este comando não executou o runtime. Este resumo limitado não substitui documentação humana.

Projeto: carteira-digital. Geração: 1.9.2; modelo: llama3.2:3b; evidência SHA-256: bd3ad12e5f7de9cda810e7df8b3c07534d5417c3d6159d17a1e37ba2b1101ff9.

Cobertura: 1/162 arquivos candidatos; explicit; 161 omitidos.

A preparação usa declarações extraídas pelo chamador e trechos delimitados pelo layout quando suportados. São auxílio determinístico, não descobertas autônomas do modelo nem verificação de runtime.

## 1

A classe AmbienteMercadoPago tem um método resolve que retorna a string do ambiente do serviço de configuração. O método verifica se o ambiente é 'teste' ou 'producao' e lança uma exceção de RuntimeException se for diferente. Os ambientes suportados são 'teste' e 'producao'.

Fonte: `app/Services/AmbienteMercadoPago.php:1`; SHA-256: `e9481dde7b0437ee6a5dbdb61b726c907396ffe7f00b0c78022b3c35b29e29de`.

    <?php
    
    namespace App\Services;
    
    use RuntimeException;
    final class AmbienteMercadoPago
    {
        public static function resolve(): string
        {
            $ambiente = config('services.mercado_pago.ambiente');
            if (! in_array($ambiente, ['teste', 'producao'], true)) {
                throw new RuntimeException('MERCADO_PAGO_AMBIENTE deve ser teste ou producao.');
            }
    
            return $ambiente;
        }
    }


