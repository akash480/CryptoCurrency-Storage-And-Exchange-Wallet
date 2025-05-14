-- Crypto Wallet and Exchange Rate Management System SQL Dump
-- Version: Custom
-- Author: You
-- Generated: 2025

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- CHARACTER SET CONFIG
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- --------------------------------------------------------
-- Database: `crypto_wallet_system`
-- --------------------------------------------------------

-- Table: users
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` TEXT NOT NULL,
  `email` TEXT NOT NULL,
  `hashed_password` TEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wallets
CREATE TABLE `wallets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `crypto_type` TEXT NOT NULL,
  `balance` DECIMAL(20,8) NOT NULL DEFAULT 0.00000000,
  `address` TEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: transactions
CREATE TABLE `transactions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `wallet_id` INT NOT NULL,
  `type` TEXT NOT NULL, -- 'send' or 'receive'
  `amount` DECIMAL(20,8) NOT NULL,
  `to_address` TEXT NOT NULL,
  `tx_hash` TEXT,
  `status` TEXT DEFAULT 'pending',
  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`wallet_id`) REFERENCES `wallets`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: exchange_rates
CREATE TABLE `exchange_rates` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `from_currency` TEXT NOT NULL,
  `to_currency` TEXT NOT NULL,
  `rate` DECIMAL(20,8) NOT NULL,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: currencies
CREATE TABLE `currencies` (
  `code` TEXT NOT NULL,
  `name` TEXT NOT NULL,
  `type` TEXT NOT NULL, -- 'crypto' or 'fiat'
  PRIMARY KEY (`code`(10)) -- Primary keys for TEXT must be length-limited
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Data (optional)

INSERT INTO `currencies` (`code`, `name`, `type`) VALUES
('BTC', 'Bitcoin', 'crypto'),
('ETH', 'Ethereum', 'crypto'),
('USDT', 'Tether', 'crypto'),
('USD', 'US Dollar', 'fiat'),
('EUR', 'Euro', 'fiat');

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
