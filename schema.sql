CREATE DATABASE IF NOT EXISTS etendering;
USE etendering;

CREATE TABLE agency (
 agency_id INT AUTO_INCREMENT PRIMARY KEY,
 agency_name VARCHAR(120) NOT NULL,
 email VARCHAR(120) NOT NULL UNIQUE,
 phone VARCHAR(20),
 address VARCHAR(255)
);

CREATE TABLE bidder (
 bidder_id INT AUTO_INCREMENT PRIMARY KEY,
 bidder_name VARCHAR(120) NOT NULL,
 email VARCHAR(120) NOT NULL UNIQUE,
 phone VARCHAR(20),
 company_name VARCHAR(150)
);

CREATE TABLE tender (
 tender_id INT AUTO_INCREMENT PRIMARY KEY,
 title VARCHAR(200) NOT NULL,
 description TEXT,
 agency_id INT,
 deadline DATE NOT NULL,
 estimated_value DECIMAL(12,2) DEFAULT 0,
 status ENUM('Open','Closed','Awarded') DEFAULT 'Open',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (agency_id) REFERENCES agency(agency_id) ON DELETE SET NULL
);

CREATE TABLE bid (
 bid_id INT AUTO_INCREMENT PRIMARY KEY,
 tender_id INT NOT NULL,
 bidder_id INT NOT NULL,
 bid_amount DECIMAL(12,2) NOT NULL,
 status ENUM('Submitted','Under Review','Accepted','Rejected') DEFAULT 'Submitted',
 submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (tender_id) REFERENCES tender(tender_id) ON DELETE CASCADE,
 FOREIGN KEY (bidder_id) REFERENCES bidder(bidder_id) ON DELETE CASCADE
);

CREATE TABLE users (
 user_id INT AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(80) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 role ENUM('admin','bidder') DEFAULT 'bidder'
);

CREATE TABLE notifications (
 notification_id INT AUTO_INCREMENT PRIMARY KEY,
 message VARCHAR(255) NOT NULL,
 tender_id INT,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (tender_id) REFERENCES tender(tender_id) ON DELETE CASCADE
);
