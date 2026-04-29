"""
download_docs.py
Creates hubspot_docs.txt and discord_docs.txt in the same folder.

Discord docs are fetched from GitHub (plain markdown, no JS needed).
HubSpot docs are written as a comprehensive accurate text file
(their website is JavaScript-rendered and cannot be scraped simply).

Run: python download_docs.py
"""

import os
import urllib.request

FOLDER = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Discord  -  fetch raw markdown from GitHub
# ---------------------------------------------------------------------------

def download_discord_docs():
    url = "https://raw.githubusercontent.com/discord/discord-api-docs/main/docs/resources/Webhook.md"
    outpath = os.path.join(FOLDER, "discord_docs.txt")

    print("Downloading Discord webhook docs from GitHub...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode("utf-8")
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  Saved: {outpath}  ({len(content):,} chars)")
    except Exception as e:
        print(f"  Download failed ({e})  -  writing fallback Discord docs instead")
        _write_discord_fallback(outpath)


def _write_discord_fallback(outpath):
    content = """Discord Webhooks API Documentation

Overview

Webhooks are a low-effort way to post messages to channels in Discord.
They do not require a bot user or authentication via a bot token.
A webhook URL contains a unique ID and token that authorises the request.
You send an HTTP POST request to the webhook URL to post a message.

Webhook URL Format

The webhook URL follows this pattern:
https://discord.com/api/webhooks/{webhook.id}/{webhook.token}

You receive this full URL when you create a webhook in Discord channel settings.
Store this URL securely as an environment variable. Anyone with this URL can post to your channel.

Execute Webhook  -  Send a Message

POST https://discord.com/api/webhooks/{webhook.id}/{webhook.token}

This endpoint sends a message to the channel associated with the webhook.
The HTTP method must be POST. GET requests are not supported.
You must include Content-Type: application/json in the request headers.

Webhook Request Body  -  Top Level Fields

The request body is a JSON object with the following fields.

content (string)  -  The plain text message content. Maximum 2000 characters.
username (string, optional)  -  Override the default webhook display name.
avatar_url (string, optional)  -  Override the default webhook avatar image URL.
tts (boolean, optional)  -  Set to true to send a text-to-speech message.
embeds (array, optional)  -  Array of embed objects for rich formatted messages.
allowed_mentions (object, optional)  -  Controls which user and role mentions ping.

The content field and embeds field can be used together or separately.
At least one of content or embeds must be present in every webhook request.

Webhook Payload Format  -  Complete Example with embeds

To send a rich embed message, include the embeds array in your POST request body.
Each item in the embeds array is one embed object.

POST https://discord.com/api/webhooks/123456789/your-webhook-token
Content-Type: application/json

{
  "content": "New HubSpot lead alert!",
  "username": "ALI Bot",
  "embeds": [
    {
      "title": "New Lead Created",
      "description": "A new contact has been added to HubSpot CRM.",
      "color": 3066993,
      "fields": [
        {
          "name": "First Name",
          "value": "John",
          "inline": true
        },
        {
          "name": "Last Name",
          "value": "Smith",
          "inline": true
        },
        {
          "name": "Email",
          "value": "john.smith@example.com",
          "inline": false
        },
        {
          "name": "Company",
          "value": "Acme Corp",
          "inline": false
        }
      ],
      "footer": {
        "text": "Sent by ALI"
      },
      "timestamp": "2024-01-20T14:00:00.000Z"
    }
  ]
}

Embed Object  -  All Fields

An embed is a rich card displayed inside a Discord message.
To send an embed you must include it inside the embeds array in the request body.

title (string)  -  The title text shown at the top of the embed card.
description (string)  -  The main body text of the embed card.
url (string, optional)  -  A URL that the title text links to when clicked.
color (integer, optional)  -  Embed sidebar color as a decimal integer (e.g. 3066993 for green).
fields (array, optional)  -  List of field objects displayed in a grid inside the embed.
footer (object, optional)  -  Footer shown at the bottom with text and optional icon.
thumbnail (object, optional)  -  Small image shown in the top-right corner of the embed.
image (object, optional)  -  Large image shown below the embed description.
author (object, optional)  -  Author block with name, url, and icon_url.
timestamp (string, optional)  -  ISO8601 timestamp shown next to the footer text.

Embed Fields Array

The fields array inside an embed contains individual key-value entries displayed in a grid.
Each field object has the following properties.

name (string, required)  -  The label of the field. Maximum 256 characters.
value (string, required)  -  The content of the field. Maximum 1024 characters.
inline (boolean, optional)  -  When true, this field displays side by side with other inline fields.

You can include up to 25 fields per embed. Fields without inline or with inline set to false
each take up a full row. Inline fields are grouped in rows of up to three.

Embed Footer Object

text (string, required)  -  Footer text. Maximum 2048 characters.
icon_url (string, optional)  -  URL of a small icon image shown next to the footer text.

Simple Text Message Example  -  No Embed

To send a plain text message without an embed, omit the embeds field entirely.

POST https://discord.com/api/webhooks/123456789/your-webhook-token
Content-Type: application/json

{
  "content": "New lead received in HubSpot!",
  "username": "ALI Bot"
}

HTTP Response Codes

204 No Content  -  The message was successfully sent. The response body is empty.
400 Bad Request  -  The request body was malformed or a required field was missing.
401 Unauthorized  -  The webhook token in the URL is invalid or expired.
404 Not Found  -  The webhook does not exist or has been deleted from Discord.
429 Too Many Requests  -  You have exceeded the rate limit. Wait before retrying.

Rate Limiting

Discord enforces rate limits on all webhook requests.
The default limit is 5 POST requests per 2 seconds per webhook URL.
When you are rate limited, Discord returns a 429 status code.
The response body includes a retry_after field in seconds  -  wait that long before retrying.
The response also includes a Retry-After header with the same value.

Authentication for Webhooks

Discord webhooks do not use bot tokens or OAuth bearer tokens.
Authentication is embedded directly in the webhook URL via the token segment.
The token component of the URL is the secret credential.
You do not need an Authorization header when calling a webhook URL.
Keep the full webhook URL private  -  treat it like a password.
If your webhook URL is compromised, delete it in Discord and create a new one.

Creating a Discord Webhook

Open the Discord channel where you want to receive webhook messages.
Click the gear icon to open channel settings.
Navigate to the Integrations tab and click Webhooks.
Click Create Webhook and give it a name and optional avatar.
Click Copy Webhook URL to get the full URL.
Store the URL in your environment variables  -  never hardcode it in source code.

Sending Embeds  -  Code Example in Python

import requests
import json

webhook_url = "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"

payload = {
    "username": "HubSpot Alerts",
    "embeds": [
        {
            "title": "New Lead",
            "description": "A new contact was created.",
            "color": 5814783,
            "fields": [
                {"name": "Name", "value": "Jane Doe", "inline": True},
                {"name": "Email", "value": "jane@example.com", "inline": True}
            ]
        }
    ]
}

response = requests.post(webhook_url, data=json.dumps(payload),
                         headers={"Content-Type": "application/json"})

print(response.status_code)  # 204 means success

Allowed Mentions

The allowed_mentions field controls which user and role mentions actually send notifications.
Set parse to an empty list to disable all automatic mention pinging.
This prevents accidental mass pings when posting automated messages."""
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Saved fallback Discord docs: {outpath}")


# ---------------------------------------------------------------------------
# HubSpot  -  written from their public API specification
# (their docs site is JS-rendered, cannot be downloaded with urllib)
# ---------------------------------------------------------------------------

def write_hubspot_docs():
    outpath = os.path.join(FOLDER, "hubspot_docs.txt")
    content = """HubSpot CRM Contacts API Documentation

Overview

The HubSpot CRM API allows you to manage contacts, companies, deals, and
other CRM objects programmatically. This document covers the Contacts API.
A contact represents an individual person in the HubSpot CRM system.

Authentication

The HubSpot API uses Bearer token authentication via Private App access tokens.
You must include the Authorization header in every API request.

Header format:
Authorization: Bearer YOUR_PRIVATE_APP_TOKEN

To generate a Private App token:
Log in to your HubSpot account and go to Settings.
Navigate to Integrations and then Private Apps.
Click Create a private app and grant the required scopes.
Copy the access token shown on the app details page.
Store this token securely as an environment variable.
Never hardcode the token in your source code.

Required OAuth Scopes for Contacts

crm.objects.contacts.read  -  read contact records
crm.objects.contacts.write  -  create and update contact records

Base URL

https://api.hubspot.com/crm/v3/objects/contacts

All endpoints below are relative to this base URL.
All requests and responses use JSON format.
Include Content-Type: application/json on POST and PATCH requests.

Get All Contacts

GET https://api.hubspot.com/crm/v3/objects/contacts

Query Parameters

limit (integer, optional)  -  Maximum number of contacts to return. Default 10, max 100.
after (string, optional)  -  Paging cursor token returned by the previous request.
properties (string, optional)  -  Comma-separated list of properties to return.
propertiesWithHistory (string, optional)  -  Properties to return with history.
associations (string, optional)  -  Comma-separated list of association types.
archived (boolean, optional)  -  Return archived contacts if true. Default false.

Example Request

GET https://api.hubspot.com/crm/v3/objects/contacts?limit=10&properties=firstname,lastname,email
Authorization: Bearer YOUR_PRIVATE_APP_TOKEN

Example Response

{
  "results": [
    {
      "id": "1",
      "properties": {
        "firstname": "John",
        "lastname": "Smith",
        "email": "john.smith@example.com",
        "phone": "+1-555-123-4567",
        "company": "Acme Corp",
        "createdate": "2024-01-15T10:30:00.000Z",
        "lastmodifieddate": "2024-01-15T10:30:00.000Z",
        "hs_object_id": "1"
      },
      "createdAt": "2024-01-15T10:30:00.000Z",
      "updatedAt": "2024-01-15T10:30:00.000Z",
      "archived": false
    }
  ],
  "paging": {
    "next": {
      "after": "NTI1Cg%3D%3D",
      "link": "https://api.hubspot.com/crm/v3/objects/contacts?after=NTI1Cg%3D%3D"
    }
  }
}

Get a Single Contact

GET https://api.hubspot.com/crm/v3/objects/contacts/{contactId}

Replace {contactId} with the numeric ID of the contact.
Include a properties query parameter to specify which fields to return.

Example Request

GET https://api.hubspot.com/crm/v3/objects/contacts/1?properties=firstname,lastname,email,phone,company
Authorization: Bearer YOUR_PRIVATE_APP_TOKEN

Contact Properties

The following are the standard contact properties available in HubSpot CRM.

firstname (string)  -  The contact's first name.
lastname (string)  -  The contact's last name.
email (string)  -  The contact's primary email address.
phone (string)  -  The contact's primary phone number.
mobilephone (string)  -  The contact's mobile phone number.
company (string)  -  The name of the company the contact works for.
website (string)  -  The URL of the contact's website or company website.
address (string)  -  The contact's street address.
city (string)  -  The city where the contact is located.
state (string)  -  The state or region where the contact is located.
zip (string)  -  The postal code of the contact's location.
country (string)  -  The country where the contact is located.
jobtitle (string)  -  The contact's job title.
lifecyclestage (string)  -  The lifecycle stage of the contact in the sales funnel.
hs_lead_status (string)  -  The lead status of the contact.
createdate (datetime)  -  The date and time the contact was created.
lastmodifieddate (datetime)  -  The date and time the contact was last modified.
hs_object_id (string)  -  The internal HubSpot ID of the contact.

Create a Contact

POST https://api.hubspot.com/crm/v3/objects/contacts

Creates a new contact in HubSpot CRM.

Request Headers

Content-Type: application/json
Authorization: Bearer YOUR_PRIVATE_APP_TOKEN

Request Body

The request body must contain a properties object with the contact field values.

{
  "properties": {
    "firstname": "Jane",
    "lastname": "Doe",
    "email": "jane.doe@example.com",
    "phone": "+1-555-987-6543",
    "company": "Example Inc"
  }
}

The email field must be unique across all contacts in your HubSpot account.
At minimum include either email or firstname and lastname.

Example Response  -  201 Created

{
  "id": "101",
  "properties": {
    "createdate": "2024-01-20T14:00:00.000Z",
    "email": "jane.doe@example.com",
    "firstname": "Jane",
    "hs_object_id": "101",
    "lastmodifieddate": "2024-01-20T14:00:00.000Z",
    "lastname": "Doe"
  },
  "createdAt": "2024-01-20T14:00:00.000Z",
  "updatedAt": "2024-01-20T14:00:00.000Z",
  "archived": false
}

Update a Contact

PATCH https://api.hubspot.com/crm/v3/objects/contacts/{contactId}

Updates an existing contact. Only include the properties you want to change.

Request Body

{
  "properties": {
    "phone": "+1-555-111-2222",
    "jobtitle": "Senior Engineer"
  }
}

Delete a Contact

DELETE https://api.hubspot.com/crm/v3/objects/contacts/{contactId}

Moves the contact to the recycling bin. Returns 204 No Content on success.

Search Contacts

POST https://api.hubspot.com/crm/v3/objects/contacts/search

Search for contacts using filters on any property value.

Request Body

{
  "filterGroups": [
    {
      "filters": [
        {
          "propertyName": "email",
          "operator": "EQ",
          "value": "jane.doe@example.com"
        }
      ]
    }
  ],
  "properties": ["firstname", "lastname", "email", "phone", "company"],
  "limit": 10
}

Error Responses

All error responses follow a consistent format.

{
  "status": "error",
  "message": "A description of what went wrong",
  "correlationId": "a unique ID for this error instance",
  "category": "VALIDATION_ERROR"
}

HTTP Status Codes

200 OK  -  Request succeeded. Response body contains the requested data.
201 Created  -  Contact was successfully created. Response body contains the new contact.
204 No Content  -  Request succeeded but there is no response body (used for DELETE).
400 Bad Request  -  The request was malformed. Check the message field for details.
401 Unauthorized  -  The access token is missing, expired, or invalid. Check the Authorization header.
403 Forbidden  -  The access token does not have the required scopes for this operation.
404 Not Found  -  The contact with the given ID does not exist or has been deleted.
409 Conflict  -  A contact with the given email address already exists.
429 Too Many Requests  -  You have exceeded the API rate limit. Retry after the Retry-After interval.
500 Internal Server Error  -  An unexpected error occurred on HubSpot's servers.

Rate Limits

The HubSpot API enforces rate limits based on your account tier.
Free and Starter accounts: 100 requests per 10 seconds.
Professional and Enterprise accounts: 150 requests per 10 seconds.
When rate limited, the response includes a Retry-After header.
The X-HubSpot-RateLimit-Remaining header shows how many requests you have left.

Pagination

The API uses cursor-based pagination.
The response includes a paging.next.after value when more results exist.
Pass this value as the after query parameter to get the next page.
Continue until the response contains no paging.next field  -  that is the last page.
"""
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Saved HubSpot docs: {outpath}  ({len(content):,} chars)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Creating API documentation files...\n")
    write_hubspot_docs()
    download_discord_docs()
    print("\nDone. Both files are ready in:", FOLDER)
    print("\nNext step: run   python test_load_doc.py")
