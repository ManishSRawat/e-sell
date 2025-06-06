import React from 'react';
import { FaShoppingCart, FaUser } from 'react-icons/fa';

function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark fixed-top" style={{ boxShadow: '0 2px 8px #0002', zIndex: 100 }}>
      <div className="container-fluid">
        {/* Logo */}
        <a className="navbar-brand fw-bold" href="/" style={{ fontSize: 24 }}>
          <span style={{ color: '#ff9900' }}>E-Shop</span>
        </a>
        {/* Category Dropdown */}
        <div className="dropdown me-2">
          <button className="btn btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
            Categories
          </button>
          <ul className="dropdown-menu">
            <li><a className="dropdown-item" href="#">Electronics</a></li>
            <li><a className="dropdown-item" href="#">Fashion</a></li>
            <li><a className="dropdown-item" href="#">Home</a></li>
            <li><a className="dropdown-item" href="#">Books</a></li>
            <li><a className="dropdown-item" href="#">More...</a></li>
          </ul>
        </div>
        {/* Search Bar */}
        <form className="d-flex flex-grow-1 mx-2" role="search">
          <input className="form-control me-2" type="search" placeholder="Search products" aria-label="Search" style={{ minWidth: 200 }} />
          <button className="btn btn-warning" type="submit">Search</button>
        </form>
        {/* Right Side: Sign-in and Cart */}
        <div className="d-flex align-items-center">
          <a href="/login" className="btn btn-outline-light me-2 d-flex align-items-center">
            <FaUser className="me-1" /> Sign In
          </a>
          <a href="/cart" className="btn btn-outline-light d-flex align-items-center position-relative">
            <FaShoppingCart className="me-1" /> Cart
            {/* Optionally, add a badge for cart count */}
            {/* <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">2</span> */}
          </a>
        </div>
      </div>
    </nav>
  );
}

export default Navbar; 