# World Hotels - Hotel Booking System

A Flask-based web application for browsing hotels, calculating dynamic pricing, and managing bookings. This project features user authentication and an administrative dashboard.

## Demo

https://github.com/user-attachments/assets/5830220b-a89b-4505-9ac8-754c6495579a

## 🚀 Features

### For Users:
- **Search & Filter**: Find hotels by city, maximum price, and availability on specific dates.
- **Dynamic Pricing**: Prices are automatically calculated based on:
  - **Seasonality**: 20% increase during peak months (April–August, November–December).
  - **Room Type**: Multipliers for Standard (1.0x), Double (1.2x), and Family (1.5x) rooms.
  - **Early Bird Discounts**: 30% off for bookings 80–90 days in advance; 20% off for 60–79 days.
- **User Authentication**: Secure signup and login system stored in a MySQL database.
- **Booking Confirmation**: Instant total price calculation and booking summary.

### For Admins:
- **Admin Dashboard**: Accessible via `/admin/login`.
- **User Management**: View a list of registered users with their details and roles.
- **Revenue Tracking**: Monitor total revenue generated from bookings.
- **Booking Overview**: See all current bookings and hotel capacities.

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, Jinja2 Templates
- **Libraries**: `mysql-connector-python`, `datetime`

## 📋 Prerequisites

- **Python 3.x**
- **MySQL Server**
- **pip** (Python package manager)

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd WDD_project
   ```

2. **Set up a Virtual Environment** (Optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install flask mysql-connector-python
   ```

4. **Database Configuration**:
   - Open your MySQL terminal or workbench.
   - Run the scripts provided in the root directory to set up the database and tables:
     ```sql
     source hotel_database.sql;
     source user_database.sql;
     ```
   - Update the database credentials in `app.py`:
     ```python
     db_config = {
         'host': 'localhost',
         'user': 'root',
         'password': 'YOUR_PASSWORD', # <--- Update this!
         'database': 'world_hotels',
         'auth_plugin': 'mysql_native_password'
     }
     ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5001`.

## 🔐 Credentials

- **Admin Login**:
  - **ID**: `admin`
  - **Password**: `password123`
- **User Login**: Create a new account via the Signup page.

## 📁 Project Structure

```text
WDD_project/
├── app.py                # Main Flask application logic
├── hotel_database.sql    # Schema for hotels and bookings
├── user_database.sql     # Schema for user accounts
├── static/               # CSS files and images
├── templates/            # HTML templates (index, login, dashboard, etc.)
└── venv/                 # Python virtual environment
```

## 📝 Note
This project is currently using a mix of MySQL for users and an in-memory list for bookings (for demonstration purposes). Future updates will fully migrate all booking data to the MySQL database.

