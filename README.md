# 🛒 APClothes eCommerce (Django Project)

A full-featured eCommerce web application built using **Python** and **Django**, supporting user authentication, product listings, shopping cart functionality, and secure online payments via Razorpay.

This project is designed to be modular, scalable, and developer-friendly — ideal as a portfolio project or base for a real-world online store.

---

## 🚀 Features

- 🔐 **User Authentication**  
  User registration, login/logout, and profile management with session handling.

- 🛍️ **Product Listings**  
  Dynamic product display with categories, pricing, and detailed views.

- 🛒 **Shopping Cart & Checkout**  
  Add/remove products, quantity update, and a smooth checkout flow.

- 💳 **Razorpay Payment Gateway Integration**  
  Seamless and secure payments in both test and live modes.

- 🧩 **Modular Django App Architecture**  
  Clean separation using Django apps: `users`, `products`, `orders`, etc.

- 🧾 **Invoice Generation** *(optional enhancement)*  
  Generate an invoice page post successful order placement.

- ✅ **Form Validation & Error Handling**  
  Server-side checks for clean, bug-free interactions during checkout.

- 📦 **Custom Django Modules**  
  For order tracking, product management, and user profile data.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Django 4+
- **Frontend**: HTML5, CSS3, Bootstrap (optional)
- **Database**: SQLite3 (default) or any supported Django DB
- **Payments**: Razorpay API
- **Deployment Ready**: Can be hosted on Render, Heroku, or any cloud service

---

## 📸 Screenshots

_Add screenshots here to showcase the UI/UX_

- Home page  
- Product listing  
- Cart page  
- Checkout with Razorpay  
- Order confirmation / invoice

---

## 📁 Project Structure

apclothes-ecommerce/
<br>
│
<br>
├── users/ # User authentication & profiles
<br>
├── products/ # Product models, views, templates
<br>
├── orders/ # Cart, Order, Checkout, Payment
<br>
├── templates/ # HTML templates
<br>
├── static/ # Static files (CSS, JS, images)
<br>
├── manage.py
<br>
└── requirements.txt
<br>
---
```bash
# 1. Clone the repository
git clone https://github.com/Aryan-parmar24/apclothes-ecommerce.git
cd apclothes-ecommerce

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # For Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up the database
python manage.py makemigrations
python manage.py migrate

# 5. Create a superuser (admin login)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver

# 7. Open in your browser
# Go to: http://127.0.0.1:8000/
```
## 💳 Razorpay Integration Notes:
Test API keys are used by default (can be found in Razorpay dashboard)
To go live, replace the test keys with live keys in your payment config
Webhook support can be added for secure server-side verification
## 🙌 Contributing
Contributions are welcome!
Feel free to fork this repo, create a feature branch, and submit a pull request (PR).

## 📃 License
This project is open-source and available under the MIT License.

## 📬 Contact
Created by Aryan Parmar
Feel free to reach out for questions, suggestions, or collaborations.




