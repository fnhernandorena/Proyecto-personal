from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

# Imports from our custom modules
from database import SessionLocal, create_db_and_tables, FinancialTransaction
from amazon_client import get_financial_transactions


def parse_and_load_data(session: Session, events: list):
    """
    Parses the raw event data from the API, transforms it into
    FinancialTransaction objects, and loads it into the database.
    """
    transactions_to_load = []
    
    for event in events:
        # Each 'event' is a dictionary that can be a ShipmentEvent, RefundEvent, etc.
        # We identify the type by checking for a key ending in 'List'.
        event_type = next((key for key in event if key.endswith('List')), None)
        if not event_type:
            continue

        # The actual list of events is nested inside this key
        event_list = event.get(event_type, [])
        for item in event_list:
            posted_date_str = item.get('PostedDate')
            posted_date = datetime.fromisoformat(posted_date_str.replace('Z', '+00:00'))

            # The structure for charges/items varies by event type.
            # This handles ShipmentEvent, RefundEvent, and similar structures.
            item_list = item.get('ShipmentItemList', item.get('ShipmentItemAdjustmentList', []))
            
            for shipment_item in item_list:
                sku = shipment_item.get('SellerSKU')
                charges = shipment_item.get('ItemChargeList', shipment_item.get('ItemChargeAdjustmentList', []))

                for charge in charges:
                    charge_type = charge.get('ChargeType')
                    amount_details = charge.get('ChargeAmount', {})
                    
                    if not all([charge_type, amount_details]):
                        continue
                    
                    quantity_shipped = shipment_item.get('QuantityShipped', 0)
                    if 'Adjustment' in event_type: 
                        quantity_shipped = -abs(quantity_shipped)

                    # Create a unique ID for the transaction to prevent duplicates
                    transaction_id = f"{item.get('AmazonOrderId', '')}-{sku}-{charge_type}-{posted_date_str}"

                    transaction = FinancialTransaction(
                        amazon_order_id=item.get('AmazonOrderId'),
                        transaction_id=transaction_id,
                        event_type=event_type.replace('List', ''),
                        posted_date=posted_date,
                        seller_sku=sku,
                        charge_type=charge_type,
                        currency_code=amount_details.get('CurrencyCode'),
                        currency_amount=Decimal(str(amount_details.get('CurrencyAmount', 0.0))),
                        quantity=quantity_shipped
                    )
                    transactions_to_load.append(transaction)

    if not transactions_to_load:
        print("No new transactions to load.")
        return

    print(f"Attempting to load {len(transactions_to_load)} parsed transactions into the database...")
    
    # Add all new objects to the session
    session.add_all(transactions_to_load)

    try:
        session.commit()
        print("Successfully committed new transactions.")
    except IntegrityError:
        print("Duplicate entries detected. Rolling back and loading one by one...")
        session.rollback()
        loaded_count = 0
        for tx in transactions_to_load:
            try:
                session.add(tx)
                session.commit()
                loaded_count += 1
            except IntegrityError:
                session.rollback() # Skip duplicate
        print(f"Successfully loaded {loaded_count} unique transactions.")
    except Exception as e:
        print(f"An error occurred during database commit: {e}")
        session.rollback()


def run_summary_report(session: Session):
    """
    Queries the database and prints a summary report of totals by SKU.
    """
    print("\n--- Summary Report: Totals by SKU ---")
    
    results = (
        session.query(
            FinancialTransaction.seller_sku,
            func.sum(FinancialTransaction.quantity).label('total_units'),
            func.sum(FinancialTransaction.currency_amount).label('total_amount'),
            func.count(FinancialTransaction.id).label('transaction_count')
        )
        .group_by(FinancialTransaction.seller_sku)
        .order_by(func.sum(FinancialTransaction.currency_amount).desc())
        .all()
    )

    if not results:
        print("No data found to generate a summary.")
        return

    print(f"{'SKU':<30} | {'TRANSACTIONS':>15} | {'TOTAL AMOUNT':>15}")
    print("-" * 65)
    for row in results:
        print(f"{row.seller_sku:<30} | {row.transaction_count:>15} | {row.total_amount:>15.2f}")
    print("-" * 65)


def main():
    """
    Main orchestration function.
    """
    print("Starting the Amazon SP-API transaction synchronization process...")

    # 1. Initialize database schema
    create_db_and_tables()

    # 2. Define date range for the query (e.g., last 7 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    print(f"Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # 3. Fetch data from Amazon SP-API
    raw_events = get_financial_transactions(start_date, end_date)

    if not raw_events:
        print("No financial events found from the API for the specified period.")
        return

    # 4. Get a database session and process the data
    db_session = SessionLocal()
    try:
        parse_and_load_data(db_session, raw_events)
        run_summary_report(db_session)
    finally:
        db_session.close()

    print("\nProcess finished successfully.")


if __name__ == "__main__":
    main()