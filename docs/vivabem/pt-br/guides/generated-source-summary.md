# Resumo do código (rascunho gerado)

As explicações do modelo exigem revisão factual e bilíngue. Citações literais foram conferidas; este comando não executou o runtime. Este resumo limitado não substitui documentação humana.

Projeto: vivabem. Geração: 1.9.2; modelo: llama3.2:3b; evidência SHA-256: 5d2abdd4c92e874a2e072c3bcaebced593a813620837d916454433daed0dd444.

Cobertura: 1/566 arquivos candidatos; explicit; 565 omitidos.

A preparação usa declarações extraídas pelo chamador e trechos delimitados pelo layout quando suportados. São auxílio determinístico, não descobertas autônomas do modelo nem verificação de runtime.

## 1

A implementação suporta a integração do Portal com o sistema existente, sem registro ou política de ambiente. A classe `PoliticaRequisicaoCofre` define constantes para o emissor, audiência e duração máxima. O método `digest` gera um hash SHA-256 do método de solicitação, caminho e corpo.

Fonte: `app/Services/PoliticaRequisicaoCofre.php:1`; SHA-256: `ea33e730fd20a157706dc2f81e043680981a8a58f55306bb0528e5e6c942e049`.

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


