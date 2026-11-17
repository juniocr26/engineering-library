# esp-hal — Blocking time conversion

Temporary reviewed partial model excerpt. Important contracts remain undocumented. Not approved for publication; source quotes and full review evidence are preserved separately.

Source revision: `e800b19c30bc208aa93d600fb158cf8cef42a4fe`.

## 1

The `Delay` struct provides methods to delay execution for specified durations or units of time, ensuring that the program waits for the specified amount of time before proceeding. The `delay` method takes a `Duration` as an argument, and the `delay_millis`, `delay_micros`, and `delay_nanos` methods take `u32` values representing milliseconds, microseconds, and nanoseconds, respectively. These methods use a `while` loop to wait for the specified duration, with the `Instant` type used to track the start time of the delay.

Source: `esp-hal/src/delay.rs:46`; SHA-256: `d1f5c5560da87be0e760bb15b9749421fb6c458c6652a721ee8618d9bf0de824`.

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


