package com.aurorabakery.configuration;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;
import org.springframework.core.env.Profiles;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.*;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

@Configuration
public class SecurityConfiguration {
    @Bean
    SecurityFilterChain security(HttpSecurity http, Environment environment, ObjectMapper mapper) throws Exception {
        return http.cors(cors -> {}).csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> {
                auth.requestMatchers(HttpMethod.GET, "/api/v1/products", "/actuator/health",
                    "/actuator/health/liveness", "/actuator/health/readiness").permitAll();
                if (environment.acceptsProfiles(Profiles.of("dev"))) {
                    auth.requestMatchers(HttpMethod.GET, "/v3/api-docs", "/v3/api-docs/**",
                        "/swagger-ui.html", "/swagger-ui/**").permitAll();
                }
                auth.anyRequest().denyAll();
            })
            .exceptionHandling(errors -> errors
                .authenticationEntryPoint((request, response, exception) -> forbidden(response, mapper))
                .accessDeniedHandler((request, response, exception) -> forbidden(response, mapper)))
            .build();
    }
    private static void forbidden(HttpServletResponse response, ObjectMapper mapper) throws IOException {
        response.setStatus(403);
        response.setContentType("application/problem+json");
        mapper.writeValue(response.getOutputStream(), ProblemDetail.forStatusAndDetail(
            HttpStatus.FORBIDDEN, "This route is not available."));
    }
    @Bean
    CorsConfigurationSource corsConfigurationSource(@Value("${app.cors.allowed-origins}") String origins) {
        var config = new CorsConfiguration();
        config.setAllowedOrigins(Arrays.stream(origins.split(",")).map(String::trim).toList());
        config.setAllowedMethods(List.of("GET"));
        config.setAllowedHeaders(List.of("Accept", "Content-Type"));
        config.setAllowCredentials(false);
        var source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", config);
        return source;
    }
}
