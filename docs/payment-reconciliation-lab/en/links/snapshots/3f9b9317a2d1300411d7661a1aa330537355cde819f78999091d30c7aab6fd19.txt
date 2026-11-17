package com.aurorabakery.catalog.application;
import com.aurorabakery.catalog.domain.Availability;
import java.math.BigDecimal;
import java.util.UUID;
public record ProductSummary(UUID id,String slug,String name,String description,BigDecimal price,String category,String imagePath,boolean featured,Availability availability,boolean purchasable) {}
