# Test local environment data
# amount_list = [1900, 1900]
# proration_list = ["false", "false"]
# quantity_list = [1, 1]
# unit_amount_list = [1900, 1900]

# Zapier input data
amount_list = input_data['amount'].split(",")
proration_list = input_data['proration'].split(",")
quantity_list = input_data['quantity'].split(",")
unit_amount_list = input_data['unit_amount'].split(",")
quantity_corrected = []
amount_decimal = []


def add_decimal(n):
    if type(n) == str:
        return float(n.replace('\U00002013', '-')) / 100
    elif type(n) == int:
        return float(n) / 100


def correct_quantity(item, proration):
    if proration == "True":
        return 1
    else:
        return item


def correct_amount(i, proration):
    if proration == "True":
        return amount_list[i]
    else:
        return unit_amount_list[i]


for i, item in enumerate(quantity_list):
    quantity = correct_quantity(item, proration_list[i])
    quantity_corrected.insert(i, quantity)
    amount = correct_amount(i, proration_list[i])
    amount_decimal.insert(i, add_decimal(amount))

output = [{'amount_decimal': amount_decimal,
           'quantity_corrected': quantity_corrected}]
print(output)
