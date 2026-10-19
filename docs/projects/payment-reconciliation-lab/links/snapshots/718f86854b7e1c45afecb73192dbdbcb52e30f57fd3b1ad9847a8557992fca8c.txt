package com.aurorabakery.configuration;

import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Reject the retired catalog seed flag until reconciliation fixtures exist. */
@Configuration
public class DevelopmentSeedConfiguration {
    @Bean
    @ConditionalOnProperty(name = "app.seed.enabled", havingValue = "true")
    ApplicationRunner unavailableDevelopmentSeed() {
        return args -> { throw new IllegalStateException(
            "DEV_SEED_ENABLED must be false: reconciliation fixtures are not implemented"); };
    }
}
