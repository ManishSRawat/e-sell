import React, { useEffect, useState } from 'react';
import { fetchProducts, filterProducts } from '../api/axios';
import { FaStar } from 'react-icons/fa';

const brands = ['Brand A', 'Brand B', 'Brand C'];

function ProductListing() {
  const [products, setProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sort, setSort] = useState('');
  const [priceRange, setPriceRange] = useState([0, 1000]);
  const [selectedBrand, setSelectedBrand] = useState('');
  const [minRating, setMinRating] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
         const data = await fetchProducts();
         setProducts(data);
      } catch (err) { console.error(err); } finally { setLoading(false); }
    })();
  }, []);

  // Filter and sort logic (client-side for demo)
  let filtered = filterProducts(products, searchTerm)
    .filter(p => p.price >= priceRange[0] && p.price <= priceRange[1])
    .filter(p => !selectedBrand || (p.brand === selectedBrand))
    .filter(p => (p.rating || 0) >= minRating);
  if (sort === 'price-asc') filtered = filtered.sort((a, b) => a.price - b.price);
  if (sort === 'price-desc') filtered = filtered.sort((a, b) => b.price - a.price);
  if (sort === 'newest') filtered = filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  return (
    <div className="container-fluid" style={{ background: '#fff', color: '#222', paddingTop: 90, minHeight: '100vh' }}>
      <div className="row mb-4">
         <div className="col-12 col-md-6 mx-auto">
            <input
               type="text"
               placeholder="Search products..."
               className="form-control"
               value={searchTerm}
               onChange={e => setSearchTerm(e.target.value)}
            />
         </div>
      </div>
      <div className="row">
         {/* Sidebar Filters */}
         <aside className="col-12 col-md-3 mb-4">
            <div className="card p-3 mb-3">
               <h5>Filters</h5>
               <div className="mb-3">
                  <label className="form-label">Price Range</label>
                  <input type="range" min="0" max="1000" value={priceRange[1]} onChange={e => setPriceRange([0, Number(e.target.value)])} className="form-range" />
                  <div>${priceRange[0]} - ${priceRange[1]}</div>
               </div>
               <div className="mb-3">
                  <label className="form-label">Brand</label>
                  <select className="form-select" value={selectedBrand} onChange={e => setSelectedBrand(e.target.value)}>
                     <option value="">All</option>
                     {brands.map(b => <option key={b} value={b}>{b}</option>)}
                  </select>
               </div>
               <div className="mb-3">
                  <label className="form-label">Min Rating</label>
                  <select className="form-select" value={minRating} onChange={e => setMinRating(Number(e.target.value))}>
                     <option value={0}>All</option>
                     {[1,2,3,4,5].map(r => <option key={r} value={r}>{r}+</option>)}
                  </select>
               </div>
            </div>
         </aside>
         {/* Main Content: Sort and Product Grid */}
         <main className="col-12 col-md-9">
            <div className="d-flex justify-content-between align-items-center mb-3">
               <h3 className="mb-0">Products</h3>
               <select className="form-select w-auto" value={sort} onChange={e => setSort(e.target.value)}>
                  <option value="">Sort By</option>
                  <option value="price-asc">Price: Low to High</option>
                  <option value="price-desc">Price: High to Low</option>
                  <option value="newest">Newest</option>
               </select>
            </div>
            {loading ? ( <div className="d-flex justify-content-center"><div className="spinner-border" role="status" /></div> ) : (
               <div className="row g-4">
                  {filtered.map(product => (
                     <div className="col-12 col-sm-6 col-md-4 col-lg-3" key={product.id}>
                        <div className="card h-100 shadow-sm product-card" style={{ transition: 'transform 0.2s' }}>
                           <img
                              src={product.images && product.images.length > 0 ? product.images[0] : 'https://via.placeholder.com/200x200?text=No+Image'}
                              className="card-img-top"
                              alt={product.name}
                              style={{ height: 180, objectFit: 'contain', background: '#f8f8f8' }}
                           />
                           <div className="card-body d-flex flex-column">
                              <h5 className="card-title" style={{ fontSize: 18 }}>{product.name}</h5>
                              <div className="mb-2">
                                 <span className="fw-bold text-success" style={{ fontSize: 16 }}>${product.price}</span>
                              </div>
                              <div className="mb-2">
                                 {[...Array(5)].map((_, i) => (
                                    <FaStar key={i} color={i < (product.rating || 0) ? '#ffc107' : '#e4e5e9'} size={16} />
                                 ))}
                              </div>
                              <a href={`/product/${product.id}`} className="btn btn-link p-0 mb-2" style={{ fontSize: 14 }}>View Details</a>
                              <button className="btn btn-warning mt-auto">Add to Cart</button>
                           </div>
                        </div>
                     </div>
                  ))}
               </div>
            )}
         </main>
      </div>
    </div>
  );
}

export default ProductListing; 