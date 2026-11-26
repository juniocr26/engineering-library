package com.aurorabakery.catalog;

import com.aurorabakery.catalog.domain.Product;
import com.aurorabakery.catalog.domain.Availability;
import com.aurorabakery.catalog.infrastructure.ProductRepository;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.*;
import java.util.List;
import java.util.UUID;
import static org.assertj.core.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@Testcontainers
@SpringBootTest(properties = {"spring.profiles.active=dev", "app.seed.enabled=false"})
@AutoConfigureMockMvc
class ProductPostgresIT {
    @Container static final PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres@sha256:639ab7ceb90e13123085b741fb31ef493fba25463002f6da665352e7b534b652");
    @DynamicPropertySource static void database(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
    @Autowired ProductRepository products;
    @Autowired JdbcTemplate jdbc;
    @Autowired MockMvc mvc;
    @BeforeEach void clear() { products.deleteAll(); }

    @Test void migrationFiltersAndOrdersRealPostgresRows() throws Exception {
        assertThat(jdbc.queryForObject("SELECT count(*) FROM flyway_schema_history WHERE success", Integer.class)).isEqualTo(2);
        products.saveAllAndFlush(List.of(product("zulu", true), product("alpha", true), product("hidden", false)));
        mvc.perform(get("/api/v1/products")).andExpect(status().isOk())
            .andExpect(jsonPath("$.length()").value(2))
            .andExpect(jsonPath("$[0].slug").value("alpha"))
            .andExpect(jsonPath("$[1].slug").value("zulu"));
    }
    @Test void unavailableRemainsVisibleButHistoricalProductsAreHidden() throws Exception {
        for (var availability : Availability.values()) {
            products.saveAndFlush(new Product(UUID.randomUUID(), availability.name().toLowerCase().replace('_','-'),
                availability.name(), new java.math.BigDecimal("10"), availability));
        }
        mvc.perform(get("/api/v1/products")).andExpect(status().isOk())
            .andExpect(jsonPath("$.length()").value(2))
            .andExpect(jsonPath("$[0].purchasable").value(true))
            .andExpect(jsonPath("$[1].purchasable").value(false));
        assertThat(products.count()).isEqualTo(4);
    }
    @Test void emptyDatabaseWorks() throws Exception {
        mvc.perform(get("/api/v1/products")).andExpect(status().isOk()).andExpect(content().json("[]"));
    }
    @Test void databaseEnforcesConstraints() {
        products.saveAndFlush(product("unique", true));
        assertThatThrownBy(() -> products.saveAndFlush(product("unique", true))).isInstanceOf(DataIntegrityViolationException.class);
        assertThatThrownBy(() -> products.saveAndFlush(product("Invalid Slug", true))).isInstanceOf(DataIntegrityViolationException.class);
        assertThatThrownBy(() -> products.saveAndFlush(new Product(UUID.randomUUID(), "blank", " ", new java.math.BigDecimal("10"), Availability.AVAILABLE)))
            .isInstanceOf(DataIntegrityViolationException.class);
    }
    @Test void operationalAndLocalDocsEndpointsWork() throws Exception {
        for (String path : List.of("/actuator/health/liveness", "/actuator/health/readiness")) {
            mvc.perform(get(path)).andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UP"))
                .andExpect(jsonPath("$.components").doesNotExist());
        }
        mvc.perform(get("/v3/api-docs")).andExpect(status().isOk())
            .andExpect(jsonPath("$.paths['/api/v1/products'].get").exists());
    }
    private Product product(String slug, boolean active) { return new Product(UUID.randomUUID(), slug, "Fictional " + slug, new java.math.BigDecimal("10"), active ? Availability.AVAILABLE : Availability.ARCHIVED); }
}
