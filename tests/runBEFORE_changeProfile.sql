-- Run before test_changeProfile.py
UPDATE user
SET postal_code_change = DATETIME(CURRENT_TIMESTAMP,'-3 months')
where id = 1; -- user id testing with
