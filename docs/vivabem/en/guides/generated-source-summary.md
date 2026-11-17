# Source summary (generated draft)

Model explanations require factual and bilingual review. Exact quotes were checked; runtime was not executed by this command. This bounded summary does not replace human documentation.

Project: vivabem. Generation: 1.9.2; model: llama3.2:3b; evidence SHA-256: 5d2abdd4c92e874a2e072c3bcaebced593a813620837d916454433daed0dd444.

Coverage: 1/566 candidate files; explicit; 565 omitted.

Evidence preparation uses caller-extracted declarations and source-layout excerpts where supported. These are deterministic assistance, not autonomous model findings or runtime verification.

## 1

The implementation supports the integration of the Portal with the existing system, without registration or environment policy. The `PoliticaRequisicaoCofre` class defines constants for the issuer, audience, and maximum duration. The `digest` method generates a SHA-256 hash of the request method, path, and body.

Source: `app/Services/PoliticaRequisicaoCofre.php:1`; SHA-256: `ea33e730fd20a157706dc2f81e043680981a8a58f55306bb0528e5e6c942e049`.

    <?php
    
    namespace App\Services;
    
    /** F06-A v1: integração existente com o Portal, sem registro nem política de ambiente. */
    final class PoliticaRequisicaoCofre
    {
        public const ISSUER = 'vivabem';
        public const AUDIENCE = 'cofre-paciente';
        public const MAX_DURATION = 60;
        public const SCOPES = [
            '/api/links/insert' => 'cofre:links:insert',
            '/api/links/get' => 'cofre:links:get',
            '/api/links/update' => 'cofre:links:update',
            '/api/cartoes-debito/insert' => 'cofre:cartoes-debito:insert',
            '/api/cartoes-debito/get' => 'cofre:cartoes-debito:get',
            '/api/cartoes-debito/delete' => 'cofre:cartoes-debito:delete',
            '/api/cartoes/insert' => 'cofre:cartoes:insert',
            '/api/cartoes/get' => 'cofre:cartoes:get',
            '/api/cartoes/delete' => 'cofre:cartoes:delete',
            '/api/avaliacoes/insert' => 'cofre:avaliacoes:insert',
            '/api/avaliacoes/avaliados' => 'cofre:avaliacoes:avaliados',
            '/api/avaliacoes/buscar-media-avaliacoes' => 'cofre:avaliacoes:buscar-media-avaliacoes',
        ];
    
        public static function digest(string $metodo, string $path, string $corpo): string
        {
            return hash('sha256', strtoupper($metodo)."\n".$path."\n".$corpo);
        }
    }


