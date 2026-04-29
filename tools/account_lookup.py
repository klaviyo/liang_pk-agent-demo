import json
from tools.klaviyo_client import get_klaviyo_client


def handle(input: dict) -> str:
    """
    Look up Klaviyo account details using the Accounts API.
    Returns account information including company name, contact info, and settings.
    """
    try:
        client = get_klaviyo_client()

        # Get account details - Klaviyo Accounts API returns info about the authenticated account
        response = client.Accounts.get_accounts(
            fields_account=[
                "contact_information",
                "industry",
                "timezone",
                "preferred_currency",
                "public_api_key"
            ]
        )

        if not response or not response.get('data'):
            return json.dumps({"error": "Unable to retrieve account information"})

        account_data = response['data'][0]['attributes']
        account_id = response['data'][0]['id']

        # Format the response to match expected structure
        result = {
            "account_id": account_id,
            "company": account_data.get('contact_information', {}).get('default_sender_name', 'N/A'),
            "email": account_data.get('contact_information', {}).get('default_sender_email', 'N/A'),
            "industry": account_data.get('industry', 'N/A'),
            "timezone": account_data.get('timezone', 'N/A'),
            "currency": account_data.get('preferred_currency', 'USD'),
            "status": "active",  # API key works, so account is active
        }

        return json.dumps(result, indent=2)

    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch account details: {str(e)}"})
