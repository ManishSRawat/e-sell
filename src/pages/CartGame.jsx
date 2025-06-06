import React, { useEffect, useRef, useState } from 'react';
import { FaShoppingCart } from 'react-icons/fa';

const ITEM_COUNT = 8;
const ITEM_SIZE = 40;
const CART_SIZE = 60;

function getRandomPosition() {
  return {
    x: Math.random() * (window.innerWidth - ITEM_SIZE),
    y: Math.random() * (window.innerHeight - ITEM_SIZE - 100) + 60,
    dx: (Math.random() - 0.5) * 2,
    dy: (Math.random() - 0.5) * 2,
    id: Math.random().toString(36).substr(2, 9)
  };
}

function isColliding(cart, item) {
  return (
    cart.x < item.x + ITEM_SIZE &&
    cart.x + CART_SIZE > item.x &&
    cart.y < item.y + ITEM_SIZE &&
    cart.y + CART_SIZE > item.y
  );
}

function CartGame() {
  const [cartPos, setCartPos] = useState({ x: 100, y: 100 });
  const [items, setItems] = useState([]);
  const requestRef = useRef();

  // Track mouse movement
  useEffect(() => {
    const handleMouseMove = (e) => {
      setCartPos({ x: e.clientX - CART_SIZE / 2, y: e.clientY - CART_SIZE / 2 });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Initialize items
  useEffect(() => {
    setItems(Array.from({ length: ITEM_COUNT }, getRandomPosition));
  }, []);

  // Animate items
  useEffect(() => {
    function animate() {
      setItems(prevItems =>
        prevItems.map(item => {
          let { x, y, dx, dy } = item;
          x += dx;
          y += dy;
          // Bounce off edges
          if (x < 0 || x > window.innerWidth - ITEM_SIZE) dx = -dx;
          if (y < 60 || y > window.innerHeight - ITEM_SIZE) dy = -dy;
          return { ...item, x: Math.max(0, Math.min(x, window.innerWidth - ITEM_SIZE)), y: Math.max(60, Math.min(y, window.innerHeight - ITEM_SIZE)), dx, dy };
        })
      );
      requestRef.current = requestAnimationFrame(animate);
    }
    requestRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(requestRef.current);
  }, []);

  // Collision detection
  useEffect(() => {
    setItems(prevItems => prevItems.filter(item => !isColliding(cartPos, item)));
  }, [cartPos]);

  return (
    <div style={{ width: '100vw', height: '100vh', overflow: 'hidden', background: '#222', position: 'fixed', top: 0, left: 0, zIndex: 1000 }}>
      {/* Items */}
      {items.map(item => (
        <div
          key={item.id}
          style={{
            position: 'absolute',
            left: item.x,
            top: item.y,
            width: ITEM_SIZE,
            height: ITEM_SIZE,
            background: 'linear-gradient(135deg, #ffec61 0%, #f321d7 100%)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontWeight: 'bold',
            fontSize: 24,
            boxShadow: '0 2px 8px #0008',
            transition: 'background 0.2s',
            zIndex: 1
          }}
        >
          🛒
        </div>
      ))}
      {/* Cart Icon */}
      <FaShoppingCart
        style={{
          position: 'absolute',
          left: cartPos.x,
          top: cartPos.y,
          width: CART_SIZE,
          height: CART_SIZE,
          color: '#00eaff',
          filter: 'drop-shadow(0 0 10px #00eaff88)',
          zIndex: 2,
          pointerEvents: 'none',
          transition: 'transform 0.1s',
        }}
      />
      {/* Instructions */}
      <div style={{ position: 'fixed', top: 10, left: 0, width: '100%', textAlign: 'center', color: '#fff', zIndex: 10 }}>
        <h2>Move your mouse to collect the items with the cart!</h2>
      </div>
    </div>
  );
}

export default CartGame; 