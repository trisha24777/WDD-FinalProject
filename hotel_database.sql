-- 1. Create the Database
CREATE DATABASE IF NOT EXISTS world_hotels;
USE world_hotels;

-- 2. Drop existing tables to ensure clean schema update
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS hotels;

-- 3. Hotels Table (Stores info from Table 1 of PDF)
CREATE TABLE hotels (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    peak_rate DECIMAL(10, 2) NOT NULL,
    off_peak_rate DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(255)
);

-- 4. Bookings Table (Relational: Links to hotels)
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT,
    user_id INT,
    room_type VARCHAR(20), -- Standard, Double, Family
    check_in DATE,
    total_price DECIMAL(10, 2),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
);

-- 5. Insert Data from Table 1 of Assessment Brief with LOCAL IMAGES
INSERT INTO hotels (city_name, capacity, peak_rate, off_peak_rate, image_url) VALUES 
('Aberdeen', 90, 140.00, 70.00, '/static/images/aberdeen.jpg'),
('Belfast', 80, 130.00, 70.00, '/static/images/belfast.jpg'),
('Birmingham', 110, 150.00, 75.00, '/static/images/birmingham.jpg'),
('Bristol', 100, 140.00, 70.00, '/static/images/bristol.jpg'),
('Cardiff', 90, 130.00, 70.00, '/static/images/cardiff.jpg'),
('Edinburgh', 120, 160.00, 80.00, '/static/images/edinburgh.jpg'),
('Glasgow', 140, 150.00, 75.00, '/static/images/glasgow.jpg'),
('London', 160, 200.00, 100.00, '/static/images/london.jpg'),
('Manchester', 150, 180.00, 90.00, '/static/images/manchester.jpg'),
('New Castle', 90, 120.00, 70.00, '/static/images/newcastle.jpg'),
('Norwich', 90, 130.00, 70.00, '/static/images/norwich.jpg'),
('Nottingham', 110, 130.00, 70.00, '/static/images/nortingham.jpg'),
('Oxford', 90, 180.00, 90.00, '/static/images/oxford.jpg'),
('Plymouth', 80, 180.00, 90.00, '/static/images/plymouth.jpg'),
('Swansea', 70, 130.00, 70.00, '/static/images/swansea.jpg'),
('Bournemouth', 90, 130.00, 70.00, '/static/images/bournemoth.jpg'),
('Kent', 100, 140.00, 80.00, '/static/images/kent.jpg');
