-- Module 40: real Class-III DSC certificates from Indian PKI CAs (e.g. ProDigiSign, eMudhra) can
-- carry Subject/Issuer Distinguished Names well over 255 characters once optional RDNs
-- (STREET, POSTALCODE, TelephoneNumber, SERIALNUMBER custom OIDs, etc.) are included - a real
-- supervisor's certificate hit this exact limit in production testing
-- (psycopg2.errors.StringDataRightTruncation on INSERT), crashing an otherwise fully verified,
-- genuinely matching signature with an uncaught HTTP 500. Widened to TEXT (no practical length
-- limit, no storage cost difference from VARCHAR(255) in Postgres for values that fit) rather than
-- a larger-but-still-bounded VARCHAR, since there is no natural upper bound on a DN string per
-- X.501 and guessing one only defers the same failure. Shared by both the Module 45
-- (IREPSSigner) and Module 40 (emBridge) signing paths, which use the same table - this is a
-- storage-capacity fix, not a change to either signing protocol.

ALTER TABLE digital_signatures ALTER COLUMN certificate_subject TYPE TEXT;
ALTER TABLE digital_signatures ALTER COLUMN certificate_issuer TYPE TEXT;
