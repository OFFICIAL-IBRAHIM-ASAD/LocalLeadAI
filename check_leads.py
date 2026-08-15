from send_campaign import get_campaign_leads
mobile, landline = get_campaign_leads()
print('Mobile (WhatsApp-ready):', len(mobile))
print('Landline (cold-call only):', len(landline))
