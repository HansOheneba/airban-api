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

        # Email to customer
        customer_email = order_data["email"]
        customer_name = order_data["customer_name"]

        # Format order items for email
        items_html = ""
        for item in order_data["items"]:
            items_html += f"""
            <tr>
                <td>{item['door_name']}</td>
                <td>{item['quantity']}</td>
                <td>GHS {item['unit_price']:.2f}</td>
                <td>GHS {item['quantity'] * item['unit_price']:.2f}</td>
            </tr>
            """

        # Send to customer
        customer_params = {
            "from": "Airban Doors <orders@hansoheneba.com>",
            "to": [customer_email],
            "subject": "Your Airban Doors Order Confirmation",
            "html": f"""
            <html>
                <body>
                    <h2>Thank you for your order, {customer_name}!</h2>
                    <p>Here are the details of your order:</p>
                    <table border="1" cellpadding="5" cellspacing="0">
                        <thead>
                            <tr>
                                <th>Door</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="3" align="right"><strong>Total:</strong></td>
                                <td><strong>GHS {order_data['total_price']:.2f}</strong></td>
                            </tr>
                        </tfoot>
                    </table>
                    <p>We'll contact you soon to confirm your order details.</p>
                    <p>If you have any questions, please reply to this email.</p>
                    <p>Best regards,<br>The Airban Doors Team</p>
                </body>
            </html>
            """,
        }

        # Send to admin (you)
        admin_params = {
            "from": "Airban Orders <orders@hansoheneba.com>",
            "to": ["hansopoku360@gmail.com"],  # Change to your admin email
            "subject": f"New Order Received from {customer_name}",
            "html": f"""
            <html>
                <body>
                    <h2>New Order Notification</h2>
                    <p>Customer: {customer_name}</p>
                    <p>Email: {customer_email}</p>
                    <p>Phone: {order_data['phone_number']}</p>
                    <p>Address: {order_data['location']}</p>
                    <p>Notes: {order_data.get('notes', 'None')}</p>
                    <p>Order Total: ${order_data['total_price']:.2f}</p>
                    
                    <h3>Order Items:</h3>
                    <table border="1" cellpadding="5" cellspacing="0">
                        <thead>
                            <tr>
                                <th>Door</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <p>Order ID: {order_data['id']}</p>
                    <p><a href="https://your-admin-dashboard.com/orders/{order_data['id']}">View in Admin Dashboard</a></p>
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
