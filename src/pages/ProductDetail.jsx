import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api/axios';

function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get(`/products/${id}`)
      .then(res => setProduct(res.data))
      .catch(() => setError('Product not found'));
  }, [id]);

  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!product) return <div>Loading...</div>;

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto' }}>
      <h2>{product.name}</h2>
      <p><strong>Price:</strong> ${product.price}</p>
      <p><strong>Description:</strong> {product.description}</p>
      <p><strong>Stock:</strong> {product.stock}</p>
      {product.images && product.images.length > 0 && (
        <div>
          <strong>Images:</strong>
          <div style={{ display: 'flex', gap: 10 }}>
            {product.images.map((img, idx) => (
              <img key={idx} src={img} alt={product.name} style={{ width: 100 }} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ProductDetail; 