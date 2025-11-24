"""
Email Notification System for Sleep Tracker
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime, timedelta


class EmailNotificationService:
    """
    Service class for sending email notifications
    """

    @staticmethod
    def send_bedtime_reminder(user, bedtime):
        """
        Send bedtime reminder email
        Args:
            user: User instance
            bedtime: Target bedtime
        Returns:
            Number of emails sent
        """
        subject = "Time for Bed!"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4A5568;">Hi {user.first_name or user.username}!</h2>
            <p style="font-size: 16px; color: #2D3748;">
                It's {bedtime.strftime('%I:%M %p')} - your target bedtime is approaching.
            </p>
            <p style="font-size: 14px; color: #4A5568;">
                Getting good sleep is important for your health and well-being.
                Consider winding down and preparing for bed soon.
            </p>
            <div style="margin-top: 30px; padding: 15px; background-color: #EDF2F7; border-radius: 5px;">
                <h3 style="color: #2D3748;">Sleep Tips:</h3>
                <ul style="color: #4A5568;">
                    <li>Put away electronic devices</li>
                    <li>Dim the lights</li>
                    <li>Practice relaxation techniques</li>
                    <li>Keep your bedroom cool and comfortable</li>
                </ul>
            </div>
            <p style="margin-top: 30px; font-size: 12px; color: #718096;">
                This is an automated reminder from your Sleep Tracker app.
            </p>
        </body>
    </html>
    """
        
        plain_content = strip_tags(html_content)

        return EmailNotificationService._send_email(
            subject=subject,
            plain_content=plain_content,
            html_content=html_content,
            to_email=user.email
        )

    @staticmethod
    def send_wake_reminder(user, wake_time):
        """
        Send wake time reminder email
        Args:
            user: User instance
            wake_time: Target wake time
        Returns:
            Number of emails sent
        """
        subject = "Good Morning!"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #4A5568;">Good morning, {user.first_name or user.username}!</h2>
                <p style="font-size: 16px; color: #2D3748;">
                    It's {wake_time.strftime('%I:%M %p')} - time to wake up and start your day!
                </p>
                <p style="font-size: 14px; color: #4A5568;">
                    Don't forget to log your sleep session in the app.
                </p>
                <div style="margin-top: 30px; padding: 15px; background-color: #EDF2F7; border-radius: 5px;">
                <h3 style="color: #2D3748;">Morning Tips:</h3>
                <ul style="color: #4A5568;">
                    <li>Expose yourself to natural light</li>
                    <li>Hydrate with a glass of water</li>
                    <li>Do some light stretching</li>
                    <li>Eat a healthy breakfast</li>
                </ul>
                </div>
                <p style="margin-top: 30px; font-size: 12px; color: #718096;">
                    This is an automated reminder from your Sleep Tracker app.
                </p>
            </body>
        </html>
        """

        plain_content = strip_tags(html_content)

        return EmailNotificationService._send_email(
            subject=subject,
            plain_content=plain_content,
            html_content=html_content,
            to_email=user.email
        )

    @staticmethod
    def send_log_reminder(user):
        """
        Send reminder to log sleep session
        Args:
            user: User instance
        Returns:
            Number of emails sent
        """
        subject = "Don't Forget to Log Your Sleep!"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4A5568;">Hi {user.first_name or user.username}!</h2>
            <p style="font-size: 16px; color: #2D3748;">
                Have you logged your sleep from last night yet?
            </p>
            <p style="font-size: 14px; color: #4A5568;">
                Tracking your sleep regularly helps you understand your sleep patterns
                and make improvements to your sleep quality.
            </p>
            <div style="margin-top: 30px; padding: 15px; background-color: #EDF2F7; border-radius: 5px;">
                <p style="color: #2D3748; margin: 0;">
                    <strong>Quick reminder:</strong> Log your bedtime, wake time, and how you felt!
                </p>
            </div>
            <p style="margin-top: 30px; font-size: 12px; color: #718096;">
                This is an automated reminder from your Sleep Tracker app.
            </p>
            </body>
        </html>
        """

        plain_content = strip_tags(html_content)

        return EmailNotificationService._send_email(
            subject=subject,
            plain_content=plain_content,
            html_content=html_content,
            to_email=user.email
        )

    @staticmethod
    def send_weekly_report(user, statistics):
        """
        Send weekly sleep report
        Args:
            user: User instance
            statistics: Dictionary with sleep statistics
        Returns:
            Number of emails sent
        """
        subject = "Your Weekly Sleep Report"

        avg_hours = statistics.get('avg_hours', 0)
        total_sessions = statistics.get('sessions', 0)
        avg_quality = statistics.get('avg_quality', 0)
        goal_achievement = statistics.get('goal_achievement', 0)

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #4A5568;">Weekly Sleep Report for {user.first_name or user.username}</h2>
                <p style="font-size: 14px; color: #718096;">
                    {datetime.now().strftime('%B %d, %Y')}
                </p>

                <div style="margin-top: 30px;">
                    <h3 style="color: #2D3748;">Your Sleep Stats This Week:</h3>
                    
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 20px;">
                        <div style="background-color: #EBF8FF; padding: 20px; border-radius: 8px; flex: 1; min-width: 200px;">
                        <h4 style="margin: 0; color: #2C5282;">Average Sleep</h4>
                        <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #2B6CB0;">
                            {avg_hours:.1f}h
                        </p>
                    </div>

                <div style="background-color: #F0FFF4; padding: 20px; border-radius: 8px; flex: 1; min-width: 200px;">
                    <h4 style="margin: 0; color: #276749;">Sleep Sessions</h4>
                    <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #2F855A;">
                        {total_sessions}
                    </p>
                </div>

                <div style="background-color: #FFFAF0; padding: 20px; border-radius: 8px; flex: 1; min-width: 200px;">
                    <h4 style="margin: 0; color: #744210;">Average Quality</h4>
                    <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #C05621;">
                        {avg_quality:.1f}/5
                    </p>
                </div>

                <div style="background-color: #FAF5FF; padding: 20px; border-radius: 8px; flex: 1; min-width: 200px;">
                    <h4 style="margin: 0; color: #553C9A;">Goal Achievement</h4>
                    <p style="font-size: 32px; font-weight: bold; margin: 10px 0; color: #6B46C1;">
                        {goal_achievement:.0f}%
                    </p>
                </div>
            </div>
        </div>

        <div style="margin-top: 30px; padding: 15px; background-color: #EDF2F7; border-radius: 5px;">
            <h3 style="color: #2D3748;">Keep It Up!</h3>
            <p style="color: #4A5568;">
                Consistency is key to better sleep. Keep tracking your sleep patterns
                to identify what works best for you.
            </p>
        </div>

        <p style="margin-top: 30px; font-size: 12px; color: #718096;">
            This is an automated weekly report from your Sleep Tracker app.
        </p>
            </body>
        </html>
        """

        plain_content = strip_tags(html_content)
        
        return EmailNotificationService._send_email(
            subject=subject,
            plain_content=plain_content,
            html_content=html_content,
            to_email=user.email
        )

    @staticmethod
    def _send_email(subject, plain_content, html_content, to_email):
        """
        Internal method to send email
        Args:
            subject: Email subject
            plain_content: Plain text content
            html_content: HTML content
            to_email: Recipient email
        Returns:
            Number of emails sent
        """
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            email.attach_alternative(html_content, "text/html")
            return email.send()
        except Exception as e:
            print(f"Error sending email: {e}")
            return 0
