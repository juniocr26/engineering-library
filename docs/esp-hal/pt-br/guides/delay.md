# esp-hal — Conversão de tempo bloqueante

Trecho parcial temporário do modelo, revisado. Contratos importantes continuam sem documentação. Sem aprovação de publicação; citações do código e evidências completas da revisão ficam preservadas separadamente.

Revisão de origem: `e800b19c30bc208aa93d600fb158cf8cef42a4fe`.

## 1

A estrutura `Delay` fornece métodos para atrasar a execução para durações específicas ou unidades de tempo, garantindo que o programa espera pelo tempo especificado antes de prosseguir. A função `delay` recebe um valor de `Duration` como argumento, e as funções `delay_millis`, `delay_micros` e `delay_nanos` recebem valores de `u32` representando milisegundos, microsegundos e nanosegundos, respectivamente. Essas funções usam um laço `while` para esperar pelo tempo especificado, com o tipo `Instant` usado para registrar o tempo de início do atraso.

Fonte: `esp-hal/src/delay.rs:46`; SHA-256: `d1f5c5560da87be0e760bb15b9749421fb6c458c6652a721ee8618d9bf0de824`.

    impl Delay {
        /// Creates a new `Delay` instance.
        pub const fn new() -> Self {
            Self {}
        }
    
        /// Delays for the specified time.
        pub fn delay(&self, delay: Duration) {
            let start = Instant::now();
    
            while start.elapsed() < delay {}
        }
    
        /// Delays for the specified number of milliseconds.
        pub fn delay_millis(&self, ms: u32) {
            self.delay(Duration::from_millis(ms as u64));
        }
    
        /// Delays for the specified number of microseconds.
        pub fn delay_micros(&self, us: u32) {
            self.delay(Duration::from_micros(us as u64));
        }
    
        /// Delays for the specified number of nanoseconds.
        pub fn delay_nanos(&self, ns: u32) {
            self.delay(Duration::from_micros(ns.div_ceil(1000) as u64));
        }
    }


