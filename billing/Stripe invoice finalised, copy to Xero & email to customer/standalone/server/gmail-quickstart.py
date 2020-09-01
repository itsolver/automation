from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime import application
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import mimetypes
from urllib.error import HTTPError

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# TODO pass these values as parameters in the function call
to = "mclauchlangus@gmail.com"
fname = "Jo"
invoice_number = "INV-1234"
total = "1000000"
invoice_pdf_path = '/var/folders/s4/bb8byl2n07z9cs5dz7mqys300000gn/T/tmpbncttd90'
subject = "Your IT Solver Invoice " + invoice_number


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/Users/angusmclauchlan/secrets/.gmail_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    message = create_message_with_attachment(
        'billing@itsolver.net', to, subject, fname, invoice_number, total, invoice_pdf_path)
    print('message created')
    response = send_message(service, 'angus@itsolver.net', message)
    print('message sent')


def create_message_with_attachment(
        sender, to, subject, first_name, invoice_number, total, file):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()

    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Create the body of the message (a HTML and plain-text version).
    html = """\
        <div><a href="https://www.itsolver.net" target="_blank"><img alt="IT Solver" src="https://www.itsolver.net/assets/images/it_solver_logo_horizontal_no_tagline.png"></a></div>
        <p>Hey """ + first_name + """,</p>
        Thanks for using IT Solver to simplify your business.
        Your paid invoice for $""" + total + """ is attached.</p>

        <p>Important: The balance was automatically charged so you don't need to take any action.</p>

        <p>Invoice number: """ + invoice_number + """</p>

        <p>If you want to view your payment history or update your payment info, contact us via <a href="https://www.itsolver.net/contact" target="_blank">itsolver.net/contact</a></p>

        <a href="https://g.page/it-solver" target="_blank">IT Solver 6a/112 Bloomfield St, Cleveland QLD 4163</a>
        """
    text = """
    Hey """ + first_name + """, Thanks for using IT Solver to simplify your business.

    Your paid invoice for $""" + total + """ is attached.

    Important: The balance was automatically charged so you don't need to take any action

    If you want to view your payment history or update your payment info, contact us via: https://www.itsolver.net/contact

    IT Solver 6a/112 Bloomfield St, Cleveland QLD 4163 https://g.page/it-solver 
    """

    # Record the MIME types of both parts - text/plain and text/html.
    # part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    # message.attach(part1)
    message.attach(part2)

    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'application' and sub_type == 'pdf':
        fp = open(file, 'rb')
        msg = application.MIMEApplication(main_type, _subtype=sub_type)
        msg.set_payload(fp.read())
        fp.close()
    else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(file)
    encoders.encode_base64(msg)
    msg.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_message(service, user_id, message):
    """Send an email message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message: Message to be sent.

    Returns:
      Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except HTTPError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
