import React, { useEffect, useState } from 'react';
import { fetchProducts, filterProducts } from '../api/axios';
import { FaStar } from 'react-icons/fa';

const banners = [
  { img: 'https://images-eu.ssl-images-amazon.com/images/G/31/img23/Fashion/GW/May/Unrec/Deals-Unrec-3000._CB557384830_.jpg', alt: 'Deal 1' },
  { img: 'https://images-eu.ssl-images-amazon.com/images/G/31/img21/OHL/GW/May/Unrec/3000x1200._CB557384830_.jpg', alt: 'Deal 2' },
  { img: 'https://images-eu.ssl-images-amazon.com/images/G/31/img23/Fashion/GW/May/Unrec/Deals-Unrec-3000._CB557384830_.jpg', alt: 'Deal 3' },
  { img: 'https://images-eu.ssl-images-amazon.com/images/G/31/img21/OHL/GW/May/Unrec/3000x1200._CB557384830_.jpg', alt: 'Deal 4' },
];

function Home() {
  const [products, setProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchProducts();
        setProducts(data);
      } catch (err) { 
        console.error(err); 
      } finally { 
        setLoading(false); 
      }
    })();
  }, []);

  const filteredProducts = filterProducts(products, searchTerm);

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
      {loading ? (
        <div className="d-flex justify-content-center">
          <div className="spinner-border" role="status" />
        </div>
      ) : (
        <div className="row g-4">
          {filteredProducts.map(product => (
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
    </div>
  );
}

export default Home;
