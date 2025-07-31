import os
import resend
from flask import current_app


def send_order_confirmation(order_data):
    """
    Send order confirmation email to customer and notification to admin
    """
    try:

        # Set the API key
        resend.api_key = current_app.config["RESEND_API_KEY"]

        # Get sender and admin email from config (from .env)
        verified_domain = current_app.config["RESEND_VERIFIED_DOMAIN"]
        admin_email = current_app.config["ADMIN_EMAIL"]

        # Email to customer
        customer_email = order_data["email"]
        customer_name = order_data["customer_name"]

        # Format order items for email
        items_html = ""
        for item in order_data["items"]:
            # Ensure unit_price is float for calculation
            unit_price = float(item["unit_price"])
            items_html += f"""
            <tr>
                <td style="padding: 8px">{item['door_name']}</td>
                <td style="padding: 8px">{item['door_type']}</td>
                <td style="padding: 8px">{item['quantity']}</td>
                <td style="padding: 8px">GHS {unit_price:.2f}</td>
                <td style="padding: 8px">GHS {item['quantity'] * unit_price:.2f}</td>
            </tr>
            """

        # Send to customer
        customer_params = {
            "from": f"Airban Doors <{verified_domain}>",
            "to": [customer_email],
            "subject": "Your Airban Doors Order Confirmation",
            "html": f"""
            <html>

<body style="margin: 0; width: 100%; padding: 0; -webkit-font-smoothing: antialiased; word-break: break-word">
  <div role="article" aria-roledescription="email" aria-label lang="en">
    <div class="sm-px-1" style="background-color: #f3f4f6; font-family: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif; font-size: 14px">
      <table align="center" style="margin: 0 auto" cellpadding="0" cellspacing="0" role="none">
        <tr>
          <td style="width: 552px; max-width: 100%">
            <div role="separator" style="line-height: 24px">&zwj;</div>
            <table style="width: 100%" cellpadding="0" cellspacing="0" role="none">
              <tr>
                <td class="sm-p-1" style="border-radius: 8px; border-width: 1px; border-color: #e5e7eb; background-color: #fffffe; padding: 24px 10px">
                  <div style="margin-bottom: 24px; display: flex; justify-content: center; border-radius: 8px; background-color: #1e3a8a; padding: 16px">
                    <img src="https://res.cloudinary.com/xenodinger/image/upload/v1753977796/airbanWhiteLogo_vau4y8.png" width="180" alt="Airban Homes Logo" style="max-width: 100%; vertical-align: middle; display: block; margin: 0 auto;">
                  </div>
                  <h1 style="margin-bottom: 8px; font-size: 18px; font-weight: 600; color: #111827">Thank You {customer_name}!</h1>
                  <p style="margin-bottom: 24px; color: #4b5563">
                    Your order has been successfully received and is currently being processed. Our team will reach out to you shortly via phone or email to confirm the details.
                    Attached to this email is a printable order receipt. Please print and keep it safe—you’ll need to present it at the time of delivery.
                  </p>
                  <h2 style="margin-bottom: 12px; font-size: 16px; font-weight: 600; color: #111827">Order Items:</h2>
                  <div style="margin-bottom: 24px; overflow-x: auto; color: #000001">
                    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 12px" cellpadding="0" cellspacing="0" role="none">
                      <thead style="background-color: #e5e7eb">
                        <tr>
                          <th style="padding: 8px">Door</th>
                          <th style="padding: 8px">Type</th>
                          <th style="padding: 8px; width: 20px">Qty</th>
                          <th style="padding: 8px">Unit Price</th>
                          <th style="padding: 8px">Total</th>
                        </tr>
                      </thead>
                      <tbody>
                       {items_html}
                      </tbody>
                    </table>
                  </div>
                  <!-- ORDER SUMMARY -->
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px; border-radius: 8px; background-color: #1e3a8a; padding: 20px; color: #ffffff; font-family: sans-serif;">
  <tr>
    <td style="">
      <h2 style="margin: 0 0 16px 0; font-size: 16px; font-weight: 700; color: #ffffff !important;">Order Summary</h2>

      <table width="100%" cellpadding="6" cellspacing="0" style="font-size: 12px; color: #ffffff;">
        <tr>
          <td style="color: #ffffff;">Customer Name</td>
          <td style="text-align: right; font-weight: 600; color: #ffffff;">{customer_name}</td>
        </tr>
        <tr>
          <td style="color: #ffffff;">Order ID</td>
          <td style="text-align: right; font-weight: 600; color: #ffffff;">{order_data['id']}</td>
        </tr>
        <tr>
          <td style="color: #ffffff;">Email</td>
          <td style="text-align: right; font-weight: 600; color: #ffffff;">{customer_email}</td>
        </tr>
        <tr>
          <td style="color: #ffffff;">Phone</td>
          <td style="text-align: right; font-weight: 600; color: #ffffff;">{order_data['phone_number']}</td>
        </tr>
        <tr>
          <td style="color: #ffffff;">Note</td>
          <td style="text-align: right; color: #ffffff;">{order_data.get('notes', 'None')}</td>
        </tr>
      </table>

      <!-- Total and Delivery Info -->
      <table width="100%" cellpadding="8" cellspacing="0" style="margin-top: 20px; border-radius: 8px; background-color: #ffffff; padding: 16px; color: #000000;">
        <tr>
          <td style="font-size: 12px; text-transform: uppercase; color: #000000;">Total</td>
          <td style="font-size: 20px; font-weight: 700; text-align: right; color: #000000;">GHS {float(order_data['total_price']):.2f}</td>
        </tr>
        <tr>
          <td style="font-size: 12px; color: #000000;">Estimated Delivery</td>
          <td style="font-size: 14px; font-weight: 500; text-align: right; color: #000000;">Aug 09, 2025</td>
        </tr>
      </table>
    </td>
  </tr>
</table>

                  <p style="margin-bottom: 4px; text-align: center; font-size: 12px; color: #6b7280">
                    Questions? Contact us at
                    <a href="mailto:sales@myairbanhomes.com" style="text-decoration: underline">sales@myairbanhomes.com</a>
                  </p>
                  <p style="text-align: center; font-size: 12px; color: #9ca3af">
                    © 2025 Airban Homes. All rights reserved.
                  </p>
                </td>
              </tr>
            </table>
            <div role="separator" style="line-height: 24px">&zwj;</div>
          </td>
        </tr>
      </table>
    </div>
  </div>
</body>
            </html>
            """,
        }

        # Send to admin (you)
        admin_params = {
            "from": f"Airban Orders <{verified_domain}>",
            "to": [admin_email],
            "subject": f"New Order Received from {customer_name}",
            "html": f"""
            <html>
               <body style="margin: 0; width: 100%; padding: 0; -webkit-font-smoothing: antialiased; word-break: break-word">
  <div role="article" aria-roledescription="email" aria-label lang="en">
    <div style="background-color: #f3f4f6; font-family: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif; font-size: 14px">
      <table align="center" cellpadding="0" cellspacing="0" style="margin: 0 auto;">
        <tr>
          <td style="width: 552px; max-width: 100%;">
            <div style="line-height: 24px">&zwj;</div>
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fffffe; border-radius: 8px; border: 1px solid #e5e7eb; padding: 24px 10px;">
              <tr>
                <td>
                  <!-- Logo -->
                  <div style="margin-bottom: 24px; display: flex; justify-content: center; border-radius: 8px; background-color: #1e3a8a; padding: 16px;">
                    <img src="https://res.cloudinary.com/xenodinger/image/upload/v1753977796/airbanWhiteLogo_vau4y8.png" width="180" alt="Airban Homes Logo" style="max-width: 100%; display: block; margin: 0 auto;">
                  </div>

                  <!-- Admin Header -->
                  <h1 style="margin-bottom: 8px; font-size: 18px; font-weight: 600; color: #111827;">New Order Received</h1>
                  <p style="margin-bottom: 24px; color: #4b5563;">
                    A new order has been placed by <strong>{customer_name}</strong>. Below are the details:
                  </p>

                  <!-- Customer Details -->
                  <table width="100%" cellpadding="6" cellspacing="0" style="font-size: 13px; color: #111827; margin-bottom: 24px;">
                    <tr>
                      <td style="font-weight: 600;">Customer Name:</td>
                      <td style="text-align: right;">{customer_name}</td>
                    </tr>
                    <tr>
                      <td style="font-weight: 600;">Email:</td>
                      <td style="text-align: right;">{customer_email}</td>
                    </tr>
                    <tr>
                      <td style="font-weight: 600;">Phone:</td>
                      <td style="text-align: right;">{order_data['phone_number']}</td>
                    </tr>
                    <tr>
                      <td style="font-weight: 600;">Address:</td>
                      <td style="text-align: right;">{order_data['location']}</td>
                    </tr>
                    <tr>
                      <td style="font-weight: 600;">Notes:</td>
                      <td style="text-align: right;">{order_data.get('notes', 'None')}</td>
                    </tr>
                  </table>

                  <!-- Order Items -->
                  <h2 style="margin-bottom: 12px; font-size: 16px; font-weight: 600; color: #111827;">Order Items:</h2>
                  <div style="margin-bottom: 24px; overflow-x: auto;">
                    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; font-size: 12px;">
                      <thead style="background-color: #e5e7eb; text-align: left;">
                        <tr>
                          <th style="padding: 8px;">Door</th>
                          <th style="padding: 8px;">Type</th>
                          <th style="padding: 8px;">Qty</th>
                          <th style="padding: 8px;">Unit Price</th>
                          <th style="padding: 8px;">Total</th>
                        </tr>
                      </thead>
                      <tbody>
                        {items_html}
                      </tbody>
                    </table>
                  </div>

                  <!-- Order Summary -->
                  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px; border-radius: 8px; background-color: #1e3a8a; padding: 20px; color: #ffffff;">
                    <tr>
                      <td>
                        <h2 style="margin: 0 0 16px 0; font-size: 16px; font-weight: 700; color: #ffffff;">Order Summary</h2>
                        <table width="100%" cellpadding="6" cellspacing="0" style="font-size: 12px;">
                          <tr>
                            <td style="color: #ffffff;">Order ID</td>
                            <td style="text-align: right; font-weight: 600; color: #ffffff;">{order_data['id']}</td>
                          </tr>
                          <tr>
                            <td style="color: #ffffff;">Order Total</td>
                            <td style="text-align: right; font-weight: 700; font-size: 14px; color: #ffffff;">GHS {float(order_data['total_price']):.2f}</td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>

                  <!-- Admin Dashboard Link -->
                  <p style="text-align: center; font-size: 13px; margin-bottom: 20px;">
                    <a href="https://airban-homes.vercel.app/admin/orders/{order_data['id']}" style="color: #1e3a8a; font-weight: 600; text-decoration: underline;">View this order in Admin Dashboard</a>
                  </p>

                  <!-- Footer -->
                  <p style="text-align: center; font-size: 12px; color: #9ca3af;">
                    © 2025 Airban Homes. Internal notification only.
                  </p>
                </td>
              </tr>
            </table>
            <div style="line-height: 24px">&zwj;</div>
          </td>
        </tr>
      </table>
    </div>
  </div>
</body>

            </html>
            """,
        }

        resend.Emails.send(customer_params)
        resend.Emails.send(admin_params)

        return True
    except Exception as e:
        current_app.logger.error(f"Error sending order emails: {str(e)}")
        return False
