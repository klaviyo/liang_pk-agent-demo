import json
from tools.klaviyo_client import get_klaviyo_client


def handle(input: dict) -> str:
    """
    Get campaign status and performance metrics using the Klaviyo Campaigns API.
    Returns campaign details, delivery stats, and performance metrics.
    """
    try:
        client = get_klaviyo_client()
        campaign_id = input.get("campaign_id")

        if campaign_id:
            # Get specific campaign details
            campaign_response = client.Campaigns.get_campaign(
                id=campaign_id,
                fields_campaign=[
                    "name",
                    "status",
                    "archived",
                    "created_at",
                    "scheduled_at",
                    "send_time"
                ]
            )

            campaign_data = campaign_response['data']['attributes']

            result = {
                "campaign_id": campaign_id,
                "name": campaign_data.get('name'),
                "status": campaign_data.get('status'),
                "created_at": campaign_data.get('created_at'),
                "scheduled_at": campaign_data.get('scheduled_at'),
                "sent_at": campaign_data.get('send_time'),
                "archived": campaign_data.get('archived')
            }

            return json.dumps(result, indent=2)

        else:
            # List recent email campaigns (filter is required by the API)
            campaigns_response = client.Campaigns.get_campaigns(
                filter="equals(messages.channel,'email')",
                fields_campaign=[
                    "name",
                    "status",
                    "archived",
                    "created_at",
                    "scheduled_at",
                    "send_time"
                ]
            )

            campaigns = []
            # Return first 20 campaigns
            for campaign in campaigns_response.get('data', [])[:20]:
                campaigns.append({
                    "campaign_id": campaign['id'],
                    "name": campaign['attributes'].get('name'),
                    "status": campaign['attributes'].get('status'),
                    "created_at": campaign['attributes'].get('created_at'),
                    "scheduled_at": campaign['attributes'].get('scheduled_at'),
                    "sent_at": campaign['attributes'].get('send_time'),
                })

            return json.dumps({
                "campaigns": campaigns,
                "total_returned": len(campaigns)
            }, indent=2)

    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch campaign data: {str(e)}"})
