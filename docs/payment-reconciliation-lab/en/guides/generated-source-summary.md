# Source summary (generated draft)

Model explanations require factual and bilingual review. Exact quotes were checked; runtime was not executed by this command. This bounded summary does not replace human documentation.

Project: payment-reconciliation-lab. Generation: 1.9.2; model: llama3.2:3b; evidence SHA-256: e831b5a6acca4d6729cf8634fdba04c3aff20e7599f424610093ec5b40d68419.

Coverage: 1/22 candidate files; explicit; 21 omitted.

Evidence preparation uses caller-extracted declarations and source-layout excerpts where supported. These are deterministic assistance, not autonomous model findings or runtime verification.

## 1

The ProductSummary record in Java supports a product with a unique identifier (UUID), slug, name, description, price, category, image path, and availability information. This record structure is used to summarize product details in the application.

Source: `backend/src/main/java/com/aurorabakery/catalog/application/ProductSummary.java:1`; SHA-256: `3f9b9317a2d1300411d7661a1aa330537355cde819f78999091d30c7aab6fd19`.

    package com.aurorabakery.catalog.application;
    import com.aurorabakery.catalog.domain.Availability;
    import java.math.BigDecimal;
    import java.util.UUID;
    public record ProductSummary(UUID id,String slug,String name,String description,BigDecimal price,String category,String imagePath,boolean featured,Availability availability,boolean purchasable) {}


