import os
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Numeric
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FinancialTransaction(Base):
    """SQLAlchemy model for the financial_transactions table."""
    __tablename__ = 'financial_transactions'

    id = Column(Integer, primary_key=True, index=True)
    amazon_order_id = Column(String, index=True, nullable=True)
    transaction_id = Column(String, index=True, unique=True)
    event_type = Column(String, nullable=False)
    posted_date = Column(DateTime, nullable=False)
    seller_sku = Column(String, index=True, nullable=True)
    charge_type = Column(String, nullable=False)
    currency_code = Column(String(3), nullable=False)
    currency_amount = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return (
            f"<FinancialTransaction(id={self.id}, "
            f"order_id='{self.amazon_order_id}', sku='{self.seller_sku}', "
            f"amount={self.currency_amount} {self.currency_code})>"
        )


def create_db_and_tables():
    """Initializes the database by creating tables defined in Base metadata."""
    Base.metadata.create_all(bind=engine)


# Allows for direct script execution to initialize the database schema.
if __name__ == "__main__":
    create_db_and_tables()