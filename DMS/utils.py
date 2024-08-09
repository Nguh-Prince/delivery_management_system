from .models import Notification, Courier, Order

def notify_courier(article):
    couriers = Courier.objects.all()
    for courier in couriers:
        message = (
            f"New article assigned:\n"
            f"Sender: {article.client.user.username}\n"
            f"Sender Address: {article.pickup_address}\n"
            f"Sender Phone: {article.sender_phone}\n"
            f"Receiver: {article.destination_address}\n"
            f"Receiver Phone: {article.receiver_phone}\n"
            f"Product Details: {', '.join([f'{p.name} ({p.description})' for p in article.products.all()])}\n"
            f"Weight: {article.weight} kg"
        )
        Notification.objects.create(
            sender=article.client.user,
            receiver=courier,  # Ensure `courier` is a `Courier` instance
            message=message
        )

    # Notify couriers about pending orders
    pending_orders = Order.objects.filter(delivery_status='Pending')
    for order in pending_orders:
        for courier in couriers:
            order_message = (
                f"Pending order #{order.id}:\n"
                f"Client: {order.client.user.username}\n"
                f"Delivery Address: {order.delivery_address}\n"
                f"Total Price: {order.total_price}\n"
                f"Please review the order details."
            )
            Notification.objects.create(
                sender=order.client.user,
                receiver=courier,  # Ensure `courier` is a `Courier` instance
                message=order_message,
                order=order  # Ensure the `order` field is optional if not required
            )
