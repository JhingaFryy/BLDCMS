from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class DigitalSignature(Base):
    __tablename__ = "digital_signatures"

    id = Column(Integer, primary_key=True, index=True)

    checksheet_id = Column(Integer, ForeignKey("checksheet_header.id", ondelete="CASCADE"), nullable=False, unique=True)

    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Denormalized at signing time, matching the rest of this codebase's convention (e.g.
    # ChecksheetHeader.technician_mobile) of keeping who-did-what readable even if the user
    # record is later renamed/deactivated.
    supervisor_name = Column(String(100), nullable=False)
    supervisor_employee_id = Column(String(20), nullable=False)

    # TEXT, not VARCHAR(N): a real Class-III DSC's Subject/Issuer Distinguished Name has no fixed
    # upper bound (X.501) and can exceed 255 characters once optional RDNs (STREET, POSTALCODE,
    # TelephoneNumber, SERIALNUMBER custom OIDs, etc.) are included - see migrations/016.
    certificate_subject = Column(Text, nullable=False)
    certificate_issuer = Column(Text, nullable=False)
    certificate_serial_number = Column(String(100), nullable=False)
    certificate_thumbprint = Column(String(128), nullable=False)
    certificate_valid_from = Column(DateTime, nullable=False)
    certificate_valid_to = Column(DateTime, nullable=False)

    signing_timestamp = Column(DateTime, nullable=False)
    signature_hash = Column(String(128), nullable=False)
    verification_status = Column(String(30), nullable=False)

    # Which signer implementation produced this signature. Current rows use "embridge" (eMudhra
    # emBridge, the sole supported signer); older rows may hold "client-local-signer", the
    # deprecated Windows-side IREPSSigner/CryptoID bridge removed in Module 41.5 - those historical
    # rows and their signed PDFs remain valid and must not be altered.
    provider = Column(String(30), nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    # uselist=False makes ChecksheetHeader.digital_signature a scalar (0-or-1), not a list - it
    # does NOT make it an inner join. Every query that eager-loads this relationship must use
    # plain joinedload()/outerjoin() (the default), never innerjoin=True, or every checksheet
    # approved before this table existed would silently disappear from any query that does.
    checksheet = relationship("ChecksheetHeader", backref=backref("digital_signature", uselist=False))
    supervisor = relationship("User", foreign_keys=[supervisor_id])
