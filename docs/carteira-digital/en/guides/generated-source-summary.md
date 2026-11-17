# Source summary (generated draft)

Model explanations require factual and bilingual review. Exact quotes were checked; runtime was not executed by this command. This bounded summary does not replace human documentation.

Project: carteira-digital. Generation: 1.9.2; model: llama3.2:3b; evidence SHA-256: bd3ad12e5f7de9cda810e7df8b3c07534d5417c3d6159d17a1e37ba2b1101ff9.

Coverage: 1/162 candidate files; explicit; 161 omitted.

Evidence preparation uses caller-extracted declarations and source-layout excerpts where supported. These are deterministic assistance, not autonomous model findings or runtime verification.

## 1

The AmbienteMercadoPago class has a resolve method that returns the environment string from the config service. The method checks if the environment is 'teste' or 'producao' and throws a RuntimeException if it's not. The supported environments are 'teste' and 'producao'.

Source: `app/Services/AmbienteMercadoPago.php:1`; SHA-256: `e9481dde7b0437ee6a5dbdb61b726c907396ffe7f00b0c78022b3c35b29e29de`.

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


