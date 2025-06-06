<<<<<<< HEAD
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
=======
# E-Commerce Website

A full-stack e-commerce platform built with Flask, MongoDB, and React.

## Features

### Phase 1 (Core)
- User Registration and Login (JWT-based)
- Admin dashboard for product management
- Product listing and details
- Shopping cart functionality
- Order placement system

### Phase 2 (Standard)
- Product categories and filters
- Search functionality
- Rating and review system
- Order history
- Inventory management

### Phase 3 (Advanced)
- Razorpay payment integration
- Email confirmations
- Coupon/discount system
- Product recommendations
- Mobile-responsive design
- Wishlist functionality
- Admin analytics

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: React, HTML, CSS, JavaScript
- **Authentication**: JWT (Flask-JWT-Extended)
- **Email**: Flask-Mail
- **Payment**: Razorpay

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with the following variables:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   MONGODB_URI=your-mongodb-uri
   JWT_SECRET_KEY=your-jwt-secret
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-email-password
   ```
5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
6. Run the development server:
   ```bash
   flask run
   ```

## Project Structure

```
ecommerce-flask/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   ├── templates/
│   ├── static/
├── config.py
├── run.py
├── requirements.txt
```

## API Documentation

API documentation will be available at `/api/docs` when running the server.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 
>>>>>>> 0abfaf033c5e8bc6cf1c4d98bde510067872a69d
