# BookLoom: E-commerce Platform for Books

BookLoom is an online bookstore built using Django and PostgreSQL, following the MVT (Model-View-Template) architecture. It provides a seamless experience for users to browse, search, and purchase books while offering an intuitive admin panel for managing products, orders, and discounts.

## Features
- **User Authentication:** Email OTP-based login and registration.
- **Admin Management:** Admin panel to manage products, categories, users, and orders.
- **Book Listings:** Display books with categories, filtering, and search functionality.
- **Cart and Checkout:** Add books to cart, apply coupons, and proceed to checkout.
- **Wallet-based Payments:** Users can make purchases using their wallet balance.
- **Razorpay Integration:** Secure online payment gateway for transactions.
- **Discounts & Offers:** Coupons, product-based and category-based offers, referral discounts.
- **Order Tracking:** View order history and track order status.
- **Email Notifications:** Order confirmations, promotions, and OTP verification.
- **Deployment:** Hosted on AWS EC2 with Nginx as a reverse proxy.

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/bookloom.git
cd bookloom
```

### 2. Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add:
```env
DEBUG=True
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_USE_TLS=True
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
```

### 5. Apply Database Migrations
```bash
python manage.py migrate
python manage.py createsuperuser  # Create an admin user
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Access the app at `http://127.0.0.1:8000/`

---

## Deployment on AWS EC2

### 1. Install Dependencies on the EC2 Instance
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv nginx
```

### 2. Clone the Repository & Set Up Virtual Environment
```bash
git clone https://github.com/your-repo/bookloom.git
cd bookloom
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 BookLoom.wsgi:application
```

### 4. Set Up Nginx Reverse Proxy
Configure `/etc/nginx/sites-available/bookloom` with:
```nginx
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/bookloom /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

---

## Future Enhancements
- Implement a recommendation engine for personalized book suggestions.
- Introduce user reviews and ratings for books.
- Add social login support (Google, Facebook, etc.).
- Enhance UI/UX with modern design improvements.

---

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

---


