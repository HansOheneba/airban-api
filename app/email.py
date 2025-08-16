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
                      Your order has been successfully received and is currently being processed. Our team will reach out to you shortly via phone or email to confirm the details and share the total cost.
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
                        <td>
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

                          <!-- Delivery Info Only -->
                          <table width="100%" cellpadding="8" cellspacing="0" style="margin-top: 20px; border-radius: 8px; background-color: #ffffff; padding: 16px; color: #000000;">
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
                              <td style="color: #ffffff;">Estimated Delivery</td>
                              <td style="text-align: right; color: #ffffff;">Aug 09, 2025</td>
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


def send_property_enquiry_emails(enquiry_data):
    """
    Send property enquiry confirmation email to customer and notification to admin
    """
    try:
        # Set the API key
        resend.api_key = current_app.config["RESEND_API_KEY"]

        # Get sender and admin email from config
        verified_domain = current_app.config["RESEND_VERIFIED_DOMAIN"]
        admin_email = current_app.config["ADMIN_EMAIL"]

        customer_email = enquiry_data["email"]
        customer_name = f"{enquiry_data['first_name']} {enquiry_data['last_name']}"

        # Send to customer
        customer_params = {
            "from": f"Airban Homes <{verified_domain}>",
            "to": [customer_email],
            "subject": "Your Property Enquiry - Airban Homes",
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
                                We have received your property enquiry and our team will get back to you within 24 hours. 
                                Below are the details of your enquiry for your records.
                              </p>
                              
                              <!-- Enquiry Details -->
                              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px; border-radius: 8px; background-color: #1e3a8a; padding: 20px; color: #ffffff;">
                                <tr>
                                  <td>
                                    <h2 style="margin: 0 0 16px 0; font-size: 16px; font-weight: 700; color: #ffffff;">Enquiry Details</h2>
                                    <table width="100%" cellpadding="6" cellspacing="0" style="font-size: 12px; color: #ffffff;">
                                      <tr>
                                        <td style="color: #ffffff;">Name</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{customer_name}</td>
                                      </tr>
                                      <tr>
                                        <td style="color: #ffffff;">Email</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{customer_email}</td>
                                      </tr>
                                      <tr>
                                        <td style="color: #ffffff;">Phone</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{enquiry_data['phone']}</td>
                                      </tr>
                                      <tr>
                                        <td style="color: #ffffff;">Property of Interest</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{enquiry_data['selected_property']}</td>
                                      </tr>
                                      <tr>
                                        <td style="color: #ffffff;">Enquiry ID</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{enquiry_data['id']}</td>
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>

                              {f'<div style="margin-bottom: 24px; padding: 16px; background-color: #f9fafb; border-radius: 8px;"><h3 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #111827;">Your Message:</h3><p style="margin: 0; color: #4b5563; font-size: 13px;">{enquiry_data.get("message", "No additional message provided")}</p></div>' if enquiry_data.get("message") else ""}

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

        # Send to admin
        admin_params = {
            "from": f"Airban Property Enquiries <{verified_domain}>",
            "to": [admin_email],
            "subject": f"New Property Enquiry from {customer_name}",
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
                              <div style="margin-bottom: 24px; display: flex; justify-content: center; border-radius: 8px; background-color: #1e3a8a; padding: 16px;">
                                <img src="https://res.cloudinary.com/xenodinger/image/upload/v1753977796/airbanWhiteLogo_vau4y8.png" width="180" alt="Airban Homes Logo" style="max-width: 100%; display: block; margin: 0 auto;">
                              </div>

                              <h1 style="margin-bottom: 8px; font-size: 18px; font-weight: 600; color: #111827;">New Property Enquiry</h1>
                              <p style="margin-bottom: 24px; color: #4b5563;">
                                A new property enquiry has been submitted by <strong>{customer_name}</strong>. Please follow up within 24 hours.
                              </p>

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
                                  <td style="text-align: right;">{enquiry_data['phone']}</td>
                                </tr>
                                <tr>
                                  <td style="font-weight: 600;">Property of Interest:</td>
                                  <td style="text-align: right;">{enquiry_data['selected_property']}</td>
                                </tr>
                                <tr>
                                  <td style="font-weight: 600;">Enquiry ID:</td>
                                  <td style="text-align: right;">{enquiry_data['id']}</td>
                                </tr>
                              </table>

                              {f'<div style="margin-bottom: 24px; padding: 16px; background-color: #f9fafb; border-radius: 8px;"><h3 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #111827;">Customer Message:</h3><p style="margin: 0; color: #4b5563; font-size: 13px;">{enquiry_data.get("message", "No additional message provided")}</p></div>' if enquiry_data.get("message") else ""}

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
        current_app.logger.error(f"Error sending property enquiry emails: {str(e)}")
        return False


def send_contact_enquiry_emails(enquiry_data):
    """
    Send contact enquiry confirmation email to customer and notification to admin
    """
    try:
        # Set the API key
        resend.api_key = current_app.config["RESEND_API_KEY"]

        # Get sender and admin email from config
        verified_domain = current_app.config["RESEND_VERIFIED_DOMAIN"]
        admin_email = current_app.config["ADMIN_EMAIL"]

        customer_email = enquiry_data["email"]
        customer_name = f"{enquiry_data['first_name']} {enquiry_data['last_name']}"

        # Send to customer
        customer_params = {
            "from": f"Airban Homes <{verified_domain}>",
            "to": [customer_email],
            "subject": "Your Contact Enquiry - Airban Homes",
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
                                We have received your contact enquiry and our team will get back to you within 24 hours. 
                                Below are the details of your enquiry for your records.
                              </p>
                              
                              <!-- Enquiry Details -->
                              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px; border-radius: 8px; background-color: #1e3a8a; padding: 20px; color: #ffffff;">
                                <tr>
                                  <td>
                                    <h2 style="margin: 0 0 16px 0; font-size: 16px; font-weight: 700; color: #ffffff;">Enquiry Details</h2>
                                    <table width="100%" cellpadding="6" cellspacing="0" style="font-size: 12px; color: #ffffff;">
                                      <tr>
                                        <td style="color: #ffffff;">Name</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{customer_name}</td>
                                      </tr>
                                      <tr>
                                        <td style="color: #ffffff;">Email</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{customer_email}</td>
                                      </tr>
                                      <tr>
                                        <td style="color: #ffffff;">Phone</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{enquiry_data['phone']}</td>
                                      </tr>
                                      <tr>
                                        <td style="color: #ffffff;">Enquiry Type</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{enquiry_data['enquiry_type']}</td>
                                      </tr>
                                      <tr>
                                        <td style="color: #ffffff;">Enquiry ID</td>
                                        <td style="text-align: right; font-weight: 600; color: #ffffff;">{enquiry_data['id']}</td>
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>

                              {f'<div style="margin-bottom: 24px; padding: 16px; background-color: #f9fafb; border-radius: 8px;"><h3 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #111827;">Additional Information:</h3><p style="margin: 0; color: #4b5563; font-size: 13px;">{enquiry_data.get("additional_info", "No additional information provided")}</p></div>' if enquiry_data.get("additional_info") else ""}

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

        # Send to admin
        admin_params = {
            "from": f"Airban Contact Enquiries <{verified_domain}>",
            "to": [admin_email],
            "subject": f"New Contact Enquiry from {customer_name} - {enquiry_data['enquiry_type']}",
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
                              <div style="margin-bottom: 24px; display: flex; justify-content: center; border-radius: 8px; background-color: #1e3a8a; padding: 16px;">
                                <img src="https://res.cloudinary.com/xenodinger/image/upload/v1753977796/airbanWhiteLogo_vau4y8.png" width="180" alt="Airban Homes Logo" style="max-width: 100%; display: block; margin: 0 auto;">
                              </div>

                              <h1 style="margin-bottom: 8px; font-size: 18px; font-weight: 600; color: #111827;">New Contact Enquiry</h1>
                              <p style="margin-bottom: 24px; color: #4b5563;">
                                A new contact enquiry has been submitted by <strong>{customer_name}</strong>. Please follow up within 24 hours.
                              </p>

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
                                  <td style="text-align: right;">{enquiry_data['phone']}</td>
                                </tr>
                                <tr>
                                  <td style="font-weight: 600;">Enquiry Type:</td>
                                  <td style="text-align: right;">{enquiry_data['enquiry_type']}</td>
                                </tr>
                                <tr>
                                  <td style="font-weight: 600;">Enquiry ID:</td>
                                  <td style="text-align: right;">{enquiry_data['id']}</td>
                                </tr>
                              </table>

                              {f'<div style="margin-bottom: 24px; padding: 16px; background-color: #f9fafb; border-radius: 8px;"><h3 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #111827;">Additional Information:</h3><p style="margin: 0; color: #4b5563; font-size: 13px;">{enquiry_data.get("additional_info", "No additional information provided")}</p></div>' if enquiry_data.get("additional_info") else ""}

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
        current_app.logger.error(f"Error sending contact enquiry emails: {str(e)}")
        return False


def send_newsletter_welcome_email(subscriber_data):
    """
    Send welcome email to new newsletter subscribers
    """
    try:
        # Set the API key
        resend.api_key = current_app.config["RESEND_API_KEY"]

        # Get sender email from config
        verified_domain = current_app.config["RESEND_VERIFIED_DOMAIN"]

        subscriber_email = subscriber_data["email"]

        subscriber_params = {
            "from": f"Airban Homes <info@myairbanhomes.com>",
            "to": [subscriber_email],
            "subject": "Welcome to Airban Homes Community",
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
                    <h1 style="margin-bottom: 8px; font-size: 18px; font-weight: 600; color: #111827">Welcome to Our Newsletter!</h1>
                    <p style="margin-bottom: 24px; color: #4b5563">
                      Thank you for expressing interest in Airban Homes! 🎉<br>
                      We're excited to have you in our community.
                    </p>
                    
                    <div style="margin-bottom: 24px; padding: 16px; background-color: #f9fafb; border-radius: 8px;">
                      <h2 style="margin: 0 0 12px 0; font-size: 16px; font-weight: 600; color: #111827;">You'll be among the first to hear about:</h2>
                      <ul style="margin: 0; padding-left: 20px; color: #4b5563;">
                        <li style="margin-bottom: 8px;">Opportunities to work and collaborate with us</li>
                        <li style="margin-bottom: 8px;">Updates on our latest projects and initiatives</li>
                        <li style="margin-bottom: 8px;">Exclusive insights into what's happening at Airban Homes</li>
                        <li style="margin-bottom: 8px;">Special promotions and early access to new services</li>
                      </ul>
                    </div>

                    <p style="margin-bottom: 24px; color: #4b5563">
                      We respect your inbox — expect only relevant updates from us.
                    </p>

                    <p style="margin-bottom: 24px; color: #4b5563">
                      In the meantime, feel free to visit our website or follow us on social media to stay connected.
                    </p>

                    <div style="margin-bottom: 24px; text-align: center;">
                      <a href="https://myairbanhomes.com" style="display: inline-block; padding: 12px 24px; background-color: #1e3a8a; color: white; text-decoration: none; border-radius: 6px; font-weight: 600;">Visit Our Website</a>
                    </div>

                    <p style="margin-bottom: 4px; text-align: center; font-size: 12px; color: #6b7280">
                      Questions? Contact us at
                      <a href="mailto:info@myairbanhomes.com" style="text-decoration: underline">info@myairbanhomes.com</a>
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

        resend.Emails.send(subscriber_params)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending newsletter welcome email: {str(e)}")
        return False


def send_newsletter_update(newsletter_data):
    """
    Send newsletter updates to subscribers
    """
    try:
        # Set the API key
        resend.api_key = current_app.config["RESEND_API_KEY"]

        # Get sender email from config
        verified_domain = current_app.config["RESEND_VERIFIED_DOMAIN"]

        subject = newsletter_data.get("subject", "Updates from Airban Homes")
        content = newsletter_data.get("content", "")
        recipient_emails = newsletter_data.get("recipients", [])

        if not recipient_emails:
            current_app.logger.error("No recipients provided for newsletter")
            return False

        # Send to all subscribers
        newsletter_params = {
            "from": f"Airban Homes <{verified_domain}>",
            "to": recipient_emails,
            "subject": subject,
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
                    
                    <div style="margin-bottom: 24px; color: #4b5563; line-height: 1.6;">
                      {content}
                    </div>

                    <div style="margin-bottom: 24px; text-align: center;">
                      <a href="https://myairbanhomes.com" style="display: inline-block; padding: 12px 24px; background-color: #1e3a8a; color: white; text-decoration: none; border-radius: 6px; font-weight: 600;">Visit Our Website</a>
                    </div>

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

        resend.Emails.send(newsletter_params)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending newsletter update: {str(e)}")
        return False
