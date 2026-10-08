# EShopping - Django E-Commerce Platform

A feature-rich e-commerce web application built using Python and Django.

## Features

- **User Authentication**: Registration, login, profile management.
- **Product Catalog**: Categorized products, featured products, product detail views.
- **Shopping Cart & Wishlist**: Add/remove products, update cart quantities, manage wishlist.
- **Checkout & Orders**: Order placement, order history, and status tracking.
- **Reviews & Ratings**: Customer reviews for products.
- **Admin Panel**: Custom administrative dashboard for managing products, categories, orders, and users.

## Tech Stack

- **Backend**: Python, Django
- **Database**: SQLite (default Django database)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap

## Getting Started

### Prerequisites

- Python 3.10+ installed

### Setup & Run

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd eshopping
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install django pillow
   ```

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Storefront: `http://127.0.0.1:8000/`
   - Admin Panel: `http://127.0.0.1:8000/admin-panel/`
