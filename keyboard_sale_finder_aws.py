import praw     # Reddit API Wrapper
import os       # Misc. Operating System Interfaces - used to read txt file
import re       # RegEx
import smtplib  # Simple Mail Transfer Protocol Client

def handler(event, context):
    # Create the Reddit instance:
    r = praw.Reddit(client_id='',
                         client_secret='',
                         password='',
                         user_agent='user_agent',
                         username='')

    # Have we run this script before? If not, create an empty list:
    path = "/tmp/threads_viewed.txt"
    if not os.path.isfile(path):
        print("First time running script, creating threads_viewed.txt")
        threads_viewed = []

    # If we have run the script before, load the file containing the posts we have already viewed:
    else:
        print("Reading threads_viewed.txt")
        # Read the file into a list and remove any empty values:
        with open(path, "r") as f:
            threads_viewed = f.read()
            threads_viewed = threads_viewed.split("\n")
            threads_viewed = list(filter(None, threads_viewed))

    change_indicator = False

    # Get the top 5 posts from /r/buildapcsales:
    subreddit = r.subreddit("buildapcsales")
    for submission in subreddit.new(limit=5):

        # If we haven't viewed this thread before:
        if submission.id not in threads_viewed:

            # Do a case insensitive search on the title and send an email if a match is found:
            if re.search("Keyboard", submission.title, re.IGNORECASE):
                print("New keyboard sale found: ")
                print(submission.title)
                print(submission.url)
                print("Id: ", submission.id)
                content = ("Subject: %s\n%s\n\n%s" % ("New Keyboard Sale!", submission.title, submission.url))
                mail = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login('AmazonSES-Username', 'AmazonSES-Password')
                try:
                    mail.sendmail('sender@email.com','receiver@email.com',content)
                    print("Successfully sent email")
                    mail.close()
                except smtplib.SMTPException:
                    print("Error: unable to send email")


            # Store the current id into our list:
            threads_viewed.append(submission.id)
            change_indicator = True

    # If no new threads exist:
    if change_indicator is False:
        print("No new keyboard sales found.")

    # Write our updated list back to the file:
    else:
        print("Updating threads_viewed.txt")
        with open(path, "w") as f:
            for post_id in threads_viewed:
                f.write(post_id + "\n")


