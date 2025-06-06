import React, { useEffect, useState } from 'react';
import api from '../api/axios';

function Cart() {
  const [cart, setCart] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('You must be logged in to view your cart.');
      return;
    }
    api.get('/cart', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => setCart(res.data))
      .catch(() => setError('Could not load cart.'));
  }, []);

  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!cart) return <div>Loading...</div>;

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto' }}>
      <h2>Your Cart</h2>
      {cart.items.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <ul>
          {cart.items.map(item => (
            <li key={item.product}>
              Product ID: {item.product} | Quantity: {item.quantity}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Cart; 