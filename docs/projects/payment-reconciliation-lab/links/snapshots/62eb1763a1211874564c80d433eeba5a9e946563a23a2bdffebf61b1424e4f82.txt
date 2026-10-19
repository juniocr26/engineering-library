import { TestBed, ComponentFixture } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ProductList } from './product-list';

describe('Bakery catalog', () => {
  let fixture: ComponentFixture<ProductList>;
  let http: HttpTestingController;
  beforeEach(() => {
    TestBed.configureTestingModule({ imports: [ProductList], providers: [provideHttpClient(), provideHttpClientTesting()] });
    http = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(ProductList);
    fixture.detectChanges();
  });
  afterEach(() => http.verify());
  it('shows loading until the request completes, then displays products', () => {
    expect(fixture.nativeElement.textContent).toContain('Loading products');
    const request = http.expectOne('/api/v1/products');
    expect(request.request.method).toBe('GET');
    request.flush([{ id: '1', slug: 'sourdough', name: 'Country sourdough', price: 24.90, purchasable: true }]);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('h2').textContent).toBe('Country sourdough');
    expect(fixture.nativeElement.textContent).not.toContain('Loading products');
  });
  it('shows price and temporary unavailability', () => {
    http.expectOne('/api/v1/products').flush([{id: '3', name: 'Strawberry cake', price: 89, purchasable: false}]);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('89.00');
    expect(fixture.nativeElement.textContent).toContain('Temporarily unavailable');
  });
  it('shows a useful empty state' , () => {
    http.expectOne('/api/v1/products').flush([]);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('No products are available');
    expect(fixture.nativeElement.querySelector('article')).toBeNull();
  });
  it('shows an error and retries through loading to success', () => {
    http.expectOne('/api/v1/products').flush({}, { status: 503, statusText: 'Unavailable' });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain("couldn't load");
    fixture.nativeElement.querySelector('button').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Loading products');
    http.expectOne('/api/v1/products').flush([{ id: '2', slug: 'cinnamon-roll', name: 'Cinnamon roll', price: 12.50, purchasable: true }]);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Cinnamon roll');
    expect(fixture.nativeElement.querySelector('[role="alert"]')).toBeNull();
  });
});
