package com.aurorabakery.catalog;

import com.aurorabakery.configuration.*;
import com.aurorabakery.catalog.api.ProductController;
import com.aurorabakery.catalog.application.*;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import java.util.List;
import java.util.UUID;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = ProductController.class, properties = "app.cors.allowed-origins=http://localhost:4200")
@Import({SecurityConfiguration.class, ApiExceptionHandler.class})
class ProductApiTest {
    @Autowired MockMvc mvc;
    @MockitoBean CatalogService service;
    @Test void publicListingReturnsExplicitDto() throws Exception {
        var id = UUID.randomUUID();
        when(service.list()).thenReturn(List.of(new ProductSummary(id,"centro","Centro","Bread",new java.math.BigDecimal("12.50"),"Bakery",null,false,com.aurorabakery.catalog.domain.Availability.AVAILABLE,true)));
        mvc.perform(get("/api/v1/products")).andExpect(status().isOk())
            .andExpect(jsonPath("$[0].id").value(id.toString()))
            .andExpect(jsonPath("$[0].slug").value("centro"))
            .andExpect(jsonPath("$[0].name").value("Centro"))
            .andExpect(jsonPath("$[0].active").doesNotExist());
    }
    @Test void emptyListingIsAnArray() throws Exception {
        when(service.list()).thenReturn(List.of());
        mvc.perform(get("/api/v1/products")).andExpect(status().isOk()).andExpect(content().json("[]"));
    }
    @Test void unmatchedAndWriteRoutesAreDenied() throws Exception {
        for (String path : List.of("/api/v1/orders", "/actuator/env", "/v3/api-docs", "/login")) {
            mvc.perform(get(path)).andExpect(status().isForbidden())
                .andExpect(content().contentTypeCompatibleWith("application/problem+json"));
        }
        mvc.perform(post("/api/v1/products")).andExpect(status().isForbidden());
    }
    @Test void onlyExplicitOriginsAreAllowed() throws Exception {
        mvc.perform(options("/api/v1/products").header("Origin", "http://localhost:4200")
            .header("Access-Control-Request-Method", "GET"))
            .andExpect(status().isOk()).andExpect(header().string("Access-Control-Allow-Origin", "http://localhost:4200"))
            .andExpect(header().doesNotExist("Access-Control-Allow-Credentials"));
        mvc.perform(options("/api/v1/products").header("Origin", "https://untrusted.example")
            .header("Access-Control-Request-Method", "GET")).andExpect(status().isForbidden());
    }
    @Test void internalErrorsDoNotLeakDetails() throws Exception {
        when(service.list()).thenThrow(new IllegalStateException("secret database password"));
        mvc.perform(get("/api/v1/products")).andExpect(status().isInternalServerError())
            .andExpect(content().contentTypeCompatibleWith("application/problem+json"))
            .andExpect(jsonPath("$.detail").value("The request could not be completed. Please try again later."))
            .andExpect(jsonPath("$.stackTrace").doesNotExist());
    }
}
