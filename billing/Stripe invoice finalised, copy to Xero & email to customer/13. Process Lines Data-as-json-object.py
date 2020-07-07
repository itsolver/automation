
# Local test data

# with open('sample-tiered-invoice.json') as json_file:
#     data = json.load(json_file)

# Zapier load Stripe raw data for finalized invoice
import json
data = json.loads(input_data['j'])

quantity_corrected = []
amount_decimal = []
descriptions = []
quantities = []
amounts = []

for j, line in enumerate(data['object']['lines']['data']):
    proration = line['proration']
    tiers_mode = line['plan']['tiers_mode']
    description = line['plan']['nickname']
    quantity = line['quantity']
    amount = None

    if tiers_mode == 'graduated':
        for tier in line['plan']['tiers']:
            tiers_flat_amount = tier['flat_amount']
            tiers_up_to = tier['up_to']
            tiers_unit_amount = tier['unit_amount']
            tiers_flat_up_to = line['plan']['tiers'][0]['up_to']
            # Flat rate tier 1
            if quantity == 0:
                print('Skipping invoice line with 0 quantity')
            elif (tiers_flat_amount != None) and (tiers_up_to != None) and (quantity > 0):
                description = description + '. Flat fee for first ' + \
                    str(tiers_up_to) + ' users'
                quantity_flat_rate = 1
                amount = tiers_flat_amount/100
                descriptions.append(description)
                quantities.append(quantity_flat_rate)
                amounts.append(amount)
            # usage under tier 1
            elif quantity < tiers_flat_up_to:
                print('Skipping')
            # Tier 2 usage
            elif (tiers_flat_amount == None) and (tiers_up_to == None) and (quantity > 0):
                description = str(line['plan']['tiers']
                                  [0]['up_to']+1) + ' and above'
                quantity_tier_2 = line['quantity'] - \
                    line['plan']['tiers'][0]['up_to']
                amount = tiers_unit_amount/100
                descriptions.append(description)
                quantities.append(quantity_tier_2)
                amounts.append(amount)

    # Non-tiered plans
    else:
        description = line['plan']['nickname']
        amount = line['amount']
        descriptions.append(description)
        quantities.append(quantity)
        amounts.append(amount)


output = [{'descriptions': descriptions,
           'quantities': quantities, 'amount_decimal': amounts}]
