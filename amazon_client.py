import os
from datetime import datetime
from dotenv import load_dotenv

from sp_api.api import Finances
from sp_api.base import SellingApiRequestThrottledException, Marketplaces
from tenacity import retry, stop_after_attempt, wait_exponential,retry_if_exception_type

# Load environment variables from .env file
load_dotenv()

# SP-API Credentials
SP_API_REFRESH_TOKEN = os.getenv("SP_API_REFRESH_TOKEN")
SP_API_CLIENT_ID = os.getenv("SP_API_CLIENT_ID")
SP_API_CLIENT_SECRET = os.getenv("SP_API_CLIENT_SECRET")
SP_API_LWA_APP_ID = os.getenv("SP_API_LWA_APP_ID")
SP_API_AWS_SECRET_KEY = os.getenv("SP_API_AWS_SECRET_KEY")
SP_API_AWS_ACCESS_KEY = os.getenv("SP_API_AWS_ACCESS_KEY")
SP_API_ROLE_ARN = os.getenv("SP_API_ROLE_ARN")


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type(SellingApiRequestThrottledException)
)
def call_sp_api(api_call, **kwargs):
    """
    Wrapper to execute SP-API calls with retry logic for throttling.
    """
    return api_call(**kwargs)


def get_financial_transactions(start_date: datetime, end_date: datetime):
    """
    Fetches all financial transactions from the SP-API within a date range.
    Handles pagination automatically to retrieve all records.

    Args:
        start_date: The start of the date range (datetime object).
        end_date: The end of the date range (datetime object).

    Returns:
        A list of all FinancialEvents dictionaries from the API response.
    """
    credentials = dict(
        refresh_token=SP_API_REFRESH_TOKEN,
        lwa_app_id=SP_API_LWA_APP_ID,
        lwa_client_id=SP_API_CLIENT_ID,
        lwa_client_secret=SP_API_CLIENT_SECRET,
        aws_secret_key=SP_API_AWS_SECRET_KEY,
        aws_access_key=SP_API_AWS_ACCESS_KEY,
        role_arn=SP_API_ROLE_ARN
    )

    finances_api = Finances(credentials=credentials, marketplace=Marketplaces.US)
    all_transactions = []
    next_token = None
    
    # Initial API call parameters
    api_params = {
        "PostedAfter": start_date.isoformat(),
        "PostedBefore": end_date.isoformat(),
    }

    while True:
        if next_token:
            api_params = {"NextToken": next_token}

        print(f"Fetching transactions... (NextToken: {str(next_token)[:20]}...)")

        try:
            response = call_sp_api(
                finances_api.list_financial_events,
                **api_params
            )
            
            payload = response.payload
            financial_events = payload.get('FinancialEvents', {})
            
            # Combine all event lists into one
            for event_list in financial_events.values():
                if isinstance(event_list, list):
                    all_transactions.extend(event_list)
            
            next_token = payload.get('NextToken')
            if not next_token:
                break # Exit loop if there are no more pages

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Depending on the error, you might want to break or handle differently
            break

    print(f"Finished fetching. Total transactions found: {len(all_transactions)}")
    return all_transactions