import smtplib, ssl


def sendEmail(stocks,email):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "brokerez411@gmail.com"
    receiver_email = "skang6283@gmail.com"
    password = "sam_411!"
    message = """\
    Subject: Hi there

    Here is a list of recommended stocks


    """+str(stocks)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
