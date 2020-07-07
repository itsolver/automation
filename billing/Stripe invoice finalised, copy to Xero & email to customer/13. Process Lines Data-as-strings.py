# Zapier Input Data
input_data = {}
input_data['quantity'] = "4,1"
input_data['amount'] = "0,10000"
input_data['proration'] = "false,false"
input_data['tiers_mode'] = "graduated,graduated"
input_data['tiers_unit_amount'] = "0,2500,0,2500"
input_data['unit_amount'] = None, None
input_data['tiers_flat_amount'] = "10000,10000"
input_data['tiers_up_to'] = "4,,4,"
tiers_data = {}
tiers_data['tiers_mode'] = input_data['tiers_mode']
print(tiers_data)
quantity_list = input_data['quantity'].split(",")
amount_list = input_data['amount'].split(",")
proration_list = input_data['proration'].split(",")
tiers_mode_list = input_data['tiers_mode'].split(",")
tiers_unit_amount_list = input_data['tiers_unit_amount'].split(",")
# match keys with quantity and replace empty values in unit_amount with 0
try:
    unit_amount_list = input_data['unit_amount'].split(",")
except:
    unit_amount_list = []
    for v in quantity_list:
        unit_amount_list.append("0")

tiers_flat_amount_list = input_data['tiers_flat_amount']
tiers_up_to_list = input_data['tiers_up_to']
# replace empty values with 0
tiers_flat_amount_list = [(int(y) if y else 0)
                          for y in tiers_flat_amount_list.split(',')]
tiers_up_to_list = [(int(x) if x else 0) for x in tiers_up_to_list.split(',')]
quantity_corrected = []
amount_decimal = []

# using list comprehension to
# perform conversion
quantity_list = [int(i) for i in quantity_list]


def add_decimal(n):
    if type(n) == str:
        return float(n.replace('\U00002013', '-')) / 100
    elif type(n) == int:
        return float(n) / 100


def correct_quantity(item, proration, tiers_mode, tiers_up_to):
    print(item, proration, tiers_mode, tiers_up_to)
    print(type(item), type(proration), type(tiers_mode), type(tiers_up_to))
    if proration == "True":
        return 1
    elif item == 0:
        return 0
    elif tiers_mode == "graduated" and tiers_up_to == 0 and item > 0:
        return item
    elif tiers_mode == "graduated" and item <= tiers_up_to:
        return 1
    else:
        return item


def correct_amount(i, proration, tiers_mode, tiers_flat_amount, tiers_unit_amount):
    print(i, proration, tiers_mode, tiers_flat_amount, tiers_unit_amount)
    print(type(proration), type(proration), type(
        tiers_flat_amount), type(tiers_unit_amount))
    if proration == "True" and tiers_mode == "graduated":
        return tiers_flat_amount
    elif tiers_unit_amount != 0 and tiers_mode == "graduated":
        return tiers_flat_amount
    elif tiers_flat_amount == 0 and tiers_unit_amount > 0:
        return tiers_unit_amount
    elif proration == "True" and tiers_mode == "":
        return amount_list[i]
    else:
        return unit_amount_list[i]


for i, item in enumerate(quantity_list):
    quantity = correct_quantity(
        int(item), proration_list[i], tiers_mode_list[i], int(tiers_up_to_list[i]))
    quantity_corrected.insert(i, quantity)
    amount = correct_amount(i, proration_list[i], tiers_mode_list[i], int(
        tiers_flat_amount_list[i]), int(tiers_unit_amount_list[i]))
    amount_decimal.insert(i, add_decimal(amount))

output = [{'amount_decimal': amount_decimal,
           'quantity_corrected': quantity_corrected}]
print(output)
