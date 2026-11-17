# Source summary (generated draft)

Model explanations require factual and bilingual review. Exact quotes were checked; runtime was not executed by this command. This bounded summary does not replace human documentation.

Project: criptografia-lib. Generation: 1.9.2; model: llama3.2:3b; evidence SHA-256: a343f94fd67febda3cfdd745bd90b1e253557e78a78f18ebfeafb2cf304d4f31.

Coverage: 1/3 candidate files; explicit; 2 omitted.

Evidence preparation uses caller-extracted declarations and source-layout excerpts where supported. These are deterministic assistance, not autonomous model findings or runtime verification.

## 1

The Configuration class validates the algorithm and private key for cryptography configuration. It checks if the algorithm is 'RS256' and the private key is not empty. If the private key is a PEM string, it is decoded and validated. The class also checks if the private key is a valid RSA private key.

Source: `src/Configuration.php:1`; SHA-256: `f3b2945336f517d5804e1c2c537a6b15930ead80f2bd200bb3bc27a22222ea33`.

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


