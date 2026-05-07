-- Database Schema for Organ Donation Tracking System
-- Generated for lecturer review

-- 1. Custom User Table (extends Django AbstractUser)
CREATE TABLE `core_user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `password` VARCHAR(128) NOT NULL,
    `last_login` DATETIME NULL,
    `is_superuser` BOOLEAN NOT NULL,
    `username` VARCHAR(150) NOT NULL UNIQUE,
    `first_name` VARCHAR(150) NOT NULL,
    `last_name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(254) NOT NULL,
    `is_staff` BOOLEAN NOT NULL,
    `is_active` BOOLEAN NOT NULL,
    `date_joined` DATETIME NOT NULL,
    `is_donor` BOOLEAN NOT NULL DEFAULT 0,
    `is_hospital` BOOLEAN NOT NULL DEFAULT 0,
    `theme` VARCHAR(20) NOT NULL DEFAULT 'dark',
    `custom_theme_color` VARCHAR(7) NOT NULL DEFAULT '#1e1e1e',
    `profile_picture` VARCHAR(100) NULL,
    `is_approved` BOOLEAN NOT NULL DEFAULT 1
);

-- 2. Donor Profile Table (1-to-1 with User)
CREATE TABLE `core_donorprofile` (
    `user_id` INT PRIMARY KEY,
    `blood_group` VARCHAR(5) NOT NULL,
    `contact_number` VARCHAR(15) NOT NULL,
    `address` TEXT NOT NULL,
    `city` VARCHAR(100) NULL,
    `state` VARCHAR(100) NULL,
    `gender` VARCHAR(10) NULL,
    `blockchain_hash` VARCHAR(255) NULL,
    `is_deceased` BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (`user_id`) REFERENCES `core_user`(`id`) ON DELETE CASCADE
);

-- 3. Hospital Profile Table (1-to-1 with User)
CREATE TABLE `core_hospitalprofile` (
    `user_id` INT PRIMARY KEY,
    `hospital_name` VARCHAR(100) NOT NULL,
    `registration_number` VARCHAR(50) NOT NULL UNIQUE,
    `contact_number` VARCHAR(15) NOT NULL,
    `address` TEXT NOT NULL,
    `city` VARCHAR(100) NULL,
    `state` VARCHAR(100) NULL,
    `blockchain_address` VARCHAR(42) NULL,
    FOREIGN KEY (`user_id`) REFERENCES `core_user`(`id`) ON DELETE CASCADE
);

-- 4. Organ Record Table
CREATE TABLE `core_organrecord` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `blockchain_id` INT NOT NULL UNIQUE,
    `organ_type` VARCHAR(50) NOT NULL,
    `blood_group` VARCHAR(5) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Available',
    `created_at` DATETIME NOT NULL,
    `donor_id` INT NOT NULL,
    `registered_by_id` INT NOT NULL,
    `recipient_hospital_id` INT NULL,
    FOREIGN KEY (`donor_id`) REFERENCES `core_donorprofile`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`registered_by_id`) REFERENCES `core_hospitalprofile`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`recipient_hospital_id`) REFERENCES `core_hospitalprofile`(`user_id`) ON DELETE SET NULL
);

-- 5. Death Certificate Table
CREATE TABLE `core_deathcertificate` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `certificate_number` VARCHAR(100) NOT NULL UNIQUE,
    `date_of_death` DATE NOT NULL,
    `cause_of_death` TEXT NOT NULL,
    `issued_at` DATETIME NOT NULL,
    `notes` TEXT NULL,
    `donor_id` INT NOT NULL,
    `issued_by_id` INT NOT NULL,
    FOREIGN KEY (`donor_id`) REFERENCES `core_donorprofile`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`issued_by_id`) REFERENCES `core_hospitalprofile`(`user_id`) ON DELETE CASCADE
);

-- 6. Feedback Table
CREATE TABLE `core_feedback` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `subject` VARCHAR(200) NOT NULL,
    `message` TEXT NOT NULL,
    `rating` INT NOT NULL DEFAULT 5,
    `submitted_at` DATETIME NOT NULL,
    `sentiment` VARCHAR(20) NULL,
    `user_id` INT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `core_user`(`id`) ON DELETE CASCADE
);
