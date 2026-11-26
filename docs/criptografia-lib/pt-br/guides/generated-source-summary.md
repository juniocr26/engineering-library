# Resumo do código (rascunho gerado)

As explicações do modelo exigem revisão factual e bilíngue. Citações literais foram conferidas; este comando não executou o runtime. Este resumo limitado não substitui documentação humana.

Projeto: criptografia-lib. Geração: 1.9.2; modelo: llama3.2:3b; evidência SHA-256: a343f94fd67febda3cfdd745bd90b1e253557e78a78f18ebfeafb2cf304d4f31.

Cobertura: 1/3 arquivos candidatos; explicit; 2 omitidos.

A preparação usa declarações extraídas pelo chamador e trechos delimitados pelo layout quando suportados. São auxílio determinístico, não descobertas autônomas do modelo nem verificação de runtime.

## 1

A classe Configuration valida o algoritmo e a chave privada para configuração de criptografia. Ela verifica se o algoritmo é 'RS256' e a chave privada não está vazia. Se a chave privada for uma string PEM, ela é decodificada e validada. A classe também verifica se a chave privada é uma chave privada RSA válida.

Fonte: `src/Configuration.php:1`; SHA-256: `f3b2945336f517d5804e1c2c537a6b15930ead80f2bd200bb3bc27a22222ea33`.

    <?php
    namespace CriptoLib;
    
    final class Configuration
    {
        public static function validate(string $algorithm, string $privateKey): void
        {
            if ($algorithm !== 'RS256') {
                throw new \InvalidArgumentException('Cryptography configuration: unsupported algorithm; expected RS256.');
            }
            if ($privateKey === '') {
                throw new \InvalidArgumentException('Cryptography configuration: private key is empty.');
            }
            $key = @openssl_pkey_get_private($privateKey);
            if ($key === false) {
                // Some historical PEM strings join the footer to the final Base64 line.
                // Reframe only an in-memory validation copy. Crypto hashes the untouched input.
                if (preg_match('/\A[ \t\r\n]*-----BEGIN (RSA PRIVATE KEY|PRIVATE KEY)-----[ \t\r\n]*([A-Za-z0-9+\/= \t\r\n]+)-----END \1-----[ \t\r\n]*\z/', $privateKey, $matches) === 1) {
                    $body = preg_replace('/[ \t\r\n]/', '', $matches[2]);
                    $der = base64_decode($body, true);
                    if ($der !== false && $der !== '') {
                        $validationPem = "-----BEGIN {$matches[1]}-----\n"
                            .chunk_split(base64_encode($der), 64, "\n")
                            ."-----END {$matches[1]}-----\n";
                        $key = @openssl_pkey_get_private($validationPem);
                    }
                }
            }
            if ($key === false || openssl_pkey_get_details($key)['type'] !== OPENSSL_KEYTYPE_RSA) {
                throw new \InvalidArgumentException('Cryptography configuration: invalid RSA private key PEM.');
            }
        }


