package com.aurorabakery.catalog.application;
import com.aurorabakery.catalog.domain.Availability;
import com.aurorabakery.catalog.infrastructure.ProductRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
@Service
public class CatalogService {
 private final ProductRepository products;
 public CatalogService(ProductRepository products){this.products=products;}
 @Transactional(readOnly=true)
 public List<ProductSummary> list(){
  return products.findByAvailabilityInOrderByFeaturedDescNameAsc(List.of(Availability.AVAILABLE,Availability.TEMPORARILY_UNAVAILABLE))
   .stream().map(p->new ProductSummary(p.getId(),p.getSlug(),p.getName(),p.getDescription(),p.getPrice(),p.getCategory(),p.getImagePath(),p.isFeatured(),p.getAvailability(),p.isPurchasable())).toList();
 }
}
