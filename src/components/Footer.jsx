import React from 'react';

function Footer() {
  return (
    <footer className="bg-dark text-light py-3 mt-5 fixed-bottom" style={{ boxShadow: '0 -2px 8px #0002' }}>
      <div className="container d-flex justify-content-between align-items-center">
        <span>&copy; {new Date().getFullYear()} E-Shop</span>
        <div>
          <a href="#" className="text-light me-3">About</a>
          <a href="#" className="text-light me-3">Help</a>
          <a href="#" className="text-light">Terms</a>
        </div>
      </div>
    </footer>
  );
}

export default Footer; 