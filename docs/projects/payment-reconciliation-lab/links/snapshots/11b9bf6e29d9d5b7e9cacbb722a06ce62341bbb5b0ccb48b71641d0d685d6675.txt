package com.aurorabakery.catalog.domain;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;
@Entity @Table(name="products")
public class Product {
 @Id private UUID id;
 @Column(nullable=false,unique=true,length=80) private String slug;
 @Column(nullable=false,length=160) private String name;
 @Column(nullable=false,length=2000) private String description;
 @Column(nullable=false,precision=12,scale=2) private BigDecimal price;
 @Column(nullable=false,length=80) private String category;
 private String imagePath;
 @Column(nullable=false) private boolean featured;
 @Enumerated(EnumType.STRING) @Column(nullable=false,length=32) private Availability availability;
 @Column(nullable=false) private Instant createdAt;
 @Column(nullable=false) private Instant updatedAt;
 protected Product() {}
 public Product(UUID id,String slug,String name,BigDecimal price,Availability availability) {
  this.id=id;this.slug=slug;this.name=name;this.price=price;this.availability=availability;
  description="Freshly baked at Aurora Bakery.";category="Bakery";createdAt=updatedAt=Instant.now();
 }
 public UUID getId(){return id;} public String getSlug(){return slug;} public String getName(){return name;}
 public String getDescription(){return description;} public BigDecimal getPrice(){return price;}
 public String getCategory(){return category;} public String getImagePath(){return imagePath;}
 public boolean isFeatured(){return featured;} public Availability getAvailability(){return availability;}
 public boolean isPurchasable(){return availability==Availability.AVAILABLE;}
}
