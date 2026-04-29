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

            # Try to get campaign report for metrics
            try:
                report_response = client.Reporting.get_campaign_report(
                    id=campaign_id,
                    fields_campaign_send_job_response=[
                        "status",
                        "progress"
                    ]
                )
                report_data = report_response.get('data', {}).get('attributes', {})
            except:
                report_data = {}

            result = {
                "campaign_id": campaign_id,
                "name": campaign_data.get('name'),
                "status": campaign_data.get('status'),
                "created_at": campaign_data.get('created_at'),
                "scheduled_at": campaign_data.get('scheduled_at'),
                "sent_at": campaign_data.get('send_time'),
                "metrics": report_data
            }

            return json.dumps(result, indent=2)

        else:
            # List recent campaigns
            campaigns_response = client.Campaigns.get_campaigns(
                filter="equals(messages.channel,'email')",
                fields_campaign=[
                    "name",
                    "status",
                    "archived",
                    "created_at",
                    "scheduled_at",
                    "send_time"
                ],
                page_size=10
            )

            campaigns = []
            for campaign in campaigns_response.get('data', []):
                campaigns.append({
                    "campaign_id": campaign['id'],
                    "name": campaign['attributes'].get('name'),
                    "status": campaign['attributes'].get('status'),
                    "created_at": campaign['attributes'].get('created_at'),
                    "scheduled_at": campaign['attributes'].get('scheduled_at'),
                    "sent_at": campaign['attributes'].get('send_time'),
                })

            return json.dumps({"campaigns": campaigns}, indent=2)

    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch campaign data: {str(e)}"})
