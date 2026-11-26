import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { App } from './app/app';

bootstrapApplication(App, {
  providers: [provideHttpClient(), provideRouter([
    { path: 'products', loadComponent: () => import('./app/catalog/product-list').then(m => m.ProductList) },
    { path: '', pathMatch: 'full', redirectTo: 'products' },
    { path: '**', redirectTo: 'products' }
  ])]
}).catch(console.error);
