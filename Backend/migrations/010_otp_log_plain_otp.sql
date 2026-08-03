-- Adds a plaintext OTP column to otp_logs, kept separate from the existing `otp` column (which
-- stores a SHA-256 hash and remains the only value ever used for verification - unchanged).
-- plain_otp exists purely so the OTP Logs Dashboard page can display the code directly to an
-- Admin/Supervisor in lieu of a real SMS/messaging gateway, and is only ever populated when
-- DEBUG=True (see app/services/otp_service.py request_otp) - the exact same condition that
-- already governs whether the plain OTP is written anywhere at all (previously only otp.log).
ALTER TABLE otp_logs ADD COLUMN IF NOT EXISTS plain_otp VARCHAR(10);
