# Antom Payment Agent

This project implements an AI-powered payment service agent that integrates Ant International's Antom payment MCP. The agent is designed to ensure secure and smooth handling of payemnts and refunds through AI interactions.

## Overview

Ant International's Antom payment MCP wraps Ant International's Antom payment APIs into standardized MCP tools, allowing AI assistants to securely process payment-related operations during conversations. With this MCP server, you can create payment sessions, query transaction status, handle refunds, and more directly through AI interactions.

The Antom Payment Agent aims to provide customers with a convenient and seamless dialogue-based payment process. it enhances the overall shopping and payment experience by flexibly organizing the payment flow according to consumer's intent using Ant International's Antom payment MCP, like initiating order checkout and cancel payment.

## Features

### 💳 Payment Operations
- **Create Payment Session** (`create_payment_session`): Generate payment sessions for client-side SDK integration
- **Query Payment Details** (`query_payment_detail`): Retrieve transaction status and information for submitted payment requests
- **Cancel Payment** (`cancel_payment`): Cancel payments when results are not returned within expected timeframes

### 💰 Refund Operations
- **Create Refund** (`create_refund`): Initiate full or partial refunds against successful payments
- **Query Refund Details** (`query_refund_detail`): Check refund status for previously submitted refund requests


## Setup and Installation


1.  **Prerequisites**

Before using the Antom Payment Agent, ensure you have:

- **Python 3.11 or higher**
- **uv** (recommended package manager) or **pip**
- **Valid Antom Merchant Account** with:
  - Merchant Client ID (CLIENT_ID)
  - Merchant RSA Private Key (MERCHANT_PRIVATE_KEY)
  - Alipay RSA Public Key (ALIPAY_PUBLIC_KEY)
  - Payment Redirect Return URL (PAYMENT_REDIRECT_URL)
  - Payment Notification Callback URL (PAYMENT_NOTIFY_URL)


2.  **Installation**


   ```bash
   # Clone this repository.
   git clone https://github.com/shear559/fabius
   cd adk-samples/python/agents/antom-payment
   # Install the package and dependencies.
   pip install poetry
   poetry install
   
   or
   uv venv 
   uv sync
   
   ```

3. **Configuration**

  You may set the following environment variables in your shell, or in a `python/agents/antom-payment/antom-payemnt-agent/.env` file instead.
   *   Set up Google Cloud credentials.

          GOOGLE_GENAI_USE_VERTEXAI
          GOOGLE_API_KEY


   *    your Antom config.


          GATEWAY_URL
          CLIENT_ID
          MERCHANT_PRIVATE_KEY
          ALIPAY_PUBLIC_KEY
          PAYMENT_REDIRECT_URL
          PAYMENT_NOTIFY_URL

## Running the Agent


**Using `adk`**


ADK provides convenient ways to bring up agents locally and interact with them.
You may talk to the agent using:

```bash
poetry run adk web
or
uv run adk web
```


**Try the following prompts:**


After running the agent, try the following example prompt

```
[user]
Create a payment link for an order called "Cream Puff" for $100 and think of a sentence describing Cream Puff.

[agent]
Sure! Here's a payment link for an order called "Cream Puff" for $100:

🔗 Payment Link:
https://open-sea-global.alipayplus.com/api/open/v1/ac/cashier/self/codevalue/checkout.htm?codeValue=https%3A%2F%2Fglobal.alipay.com%2F281002040096G2MGzTTyy0bKXR6HrRDv4Icb

And here's a sentence describing the Cream Puff:

"Indulge in our heavenly Cream Puff — a delicate, golden shell filled with silky vanilla custard and a hint of caramel, perfect for any sweet craving."

Let me know if you want help generating a real payment link using a specific service!
```