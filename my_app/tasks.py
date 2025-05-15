# my_app/tasks.py
from celery import shared_task

@shared_task
def send_review_notification_email(username, product_name, review_content, rating):
    # You can customize the email logic here
    subject = f"New Review for {product_name}"
    message = f"User {username} left a review:\n\n{review_content}\n\nRating: {rating}"
    admin_email = "albineldho81@gmail.com"

    # Simulate sending email (or use Django's send_mail)
    print(f"Sending email to {admin_email}")
    print("Subject:", subject)
    print("Message:", message)
