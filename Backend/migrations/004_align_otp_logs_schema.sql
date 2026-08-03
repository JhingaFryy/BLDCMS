-- Align otp_logs with the SQLAlchemy OTPLog model without dropping or recreating the table

ALTER TABLE otp_logs
    ALTER COLUMN id SET DEFAULT nextval('otp_logs_id_seq'::regclass);

ALTER TABLE otp_logs
    ALTER COLUMN user_id SET NOT NULL;

ALTER TABLE otp_logs
    ALTER COLUMN otp SET NOT NULL;

ALTER TABLE otp_logs
    ALTER COLUMN expires_at SET NOT NULL;

ALTER TABLE otp_logs
    ALTER COLUMN is_verified SET DEFAULT false;

ALTER TABLE otp_logs
    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE otp_logs
    ADD COLUMN IF NOT EXISTS attempts INTEGER;

UPDATE otp_logs
SET attempts = 0
WHERE attempts IS NULL;

ALTER TABLE otp_logs
    ALTER COLUMN attempts SET DEFAULT 0,
    ALTER COLUMN attempts SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND indexname = 'ix_otp_logs_id'
    ) THEN
        CREATE INDEX ix_otp_logs_id ON public.otp_logs (id);
    END IF;
END $$;
