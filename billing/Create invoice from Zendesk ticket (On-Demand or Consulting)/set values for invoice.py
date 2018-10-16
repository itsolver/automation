# If ticket requester in organisation, only populate organisation field and  don't populate email field. Otherwise, for individual requester grab name and email.
try:
    input_data['reqorg']
    contact = input_data['reqorg']
    email = ""
except:
    contact = input_data['reqname']
    email = input_data['reqemail']
    
# Switch case to determine hourly rate based on support type.
def getinvoiceline(reqtype):
    return {
        'remote': "On-demand Support is $179 per request.",
        'carry_in': "On-demand Support is $179 per request.",
        'consultation': "Consultation is $120 per hour. Free call out within the Redlands.",
        'on_site': "On-demand Support is $179 per request.",
        'meeting_point': "On-demand Support is $179 per request."
    }.get(reqtype, "On-demand Support is $179 per request.")

# Switch case to determine correct sales account.
def getsalesaccount(reqtype):
    return {
        'remote': "249",
        'carry_in': "249",
        'consultation': "245",
        'on_site': "249",
        'meeting_point': "249"
    }.get(reqtype, "249")

# Round up to nearest .25 (for 15 minute blocks)
def x_round(x):
    return math.ceil(x*4)/4

# Get quantity for consultation jobs
def get_time(number):
    try: 
        number = float(inp)
        if number > 3600:
            return x_round(number) # Bill in 15 minute blocks
        else:
            return 1 # Minimum 1 hour for consultation
    except ValueError:
        return 1 # No time recorded, assume we're doing 1 x On-Demand Support
   
# Set sales account and price accordingly. Change quantity to 1 if it's On-Demand Support.
salesaccount = getsalesaccount(input_data['reqtype'])
if salesaccount == "245":
    price = "120" # $120 per hour for consultation
    inp = input_data['timeseconds'] 
    quantity = get_time(inp) # Set billable hours
else: 
    salesaccount = "249" # If not Consultation, Change Sales Account to On-Demand Support
    price = "179" # $179 per On-Demand Support Request
    quantity = "1"
    
# Set values for Xero invoice
invoiceline = getinvoiceline(input_data['reqtype'])
output = [{'contact': contact, 'email': email, 'invoiceline': invoiceline, 'salesaccount': salesaccount, 'quantity': quantity, 'price': price}]