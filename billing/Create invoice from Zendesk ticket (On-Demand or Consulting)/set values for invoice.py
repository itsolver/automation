# If ticket requester in organisation, only populate organisation field and  don't populate email field. Otherwise, for individual requester grab name and email.
try:
    input_data['reqorg']
    contact = input_data['reqorg']
    email = ""
except:
    contact = input_data['reqname']
    email = input_data['reqemail']
    
# Set values for Xero invoice
output = [{'contact': contact, 'email': email}]