package com.aurorabakery.catalog.api;
import com.aurorabakery.catalog.application.*;
import org.springframework.web.bind.annotation.*;
import java.util.List;
@RestController @RequestMapping("/api/v1/products")
public class ProductController {
 private final CatalogService catalog;
 public ProductController(CatalogService catalog){this.catalog=catalog;}
 @GetMapping public List<ProductSummary> list(){return catalog.list();}
}
