import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface Product { id: string; slug: string; name: string; description: string; price: number; category: string; featured: boolean; availability: string; purchasable: boolean; }

@Injectable({ providedIn: 'root' })
export class ProductApi {
  private readonly http = inject(HttpClient);
  list() { return this.http.get<Product[]>('/api/v1/products'); }
}
