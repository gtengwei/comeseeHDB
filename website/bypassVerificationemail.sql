-- SQLite
UPDATE user
SET email_verified = 1, email_verified_date = datetime('now','localtime')
WHERE email = 'yeophuenyeo@gmail.com';