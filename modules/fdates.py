
# e.g. format string: "day-month-year"

# e.g. date_string = "15-05-2001"

def parse(format, date_string, normalize=False):

    import re

    keywords = {
        "month": parse_month,
        "day": parse_day,
        "year": parse_year
    }

    # keywords = {
    #     "month": monthindex,
    #     "day": "test",
    #     "year": "test"
    # }

    keyword_indexes = {} # where each keyword occurs
    to_regex = format

    for triggerword in keywords.keys():
        keyword_indexes[triggerword] = [m.start() for m in re.finditer(triggerword, format)]
        to_regex = to_regex.replace(triggerword, "(.*)")

    results = re.finditer(r"{}".format(to_regex), date_string)
    match_data = False

    for r in results: match_data = r.groups()

    if match_data == False: return False

    # print(keyword_indexes)
    # print(match_data)

    # for result in results:
    #     match_data = result.groups()
    # last_claim_index = 0
    last_bottom_check = 99999
    claimed_indexes = []
    order_of_operations = []
    # iterating through each piece of data and figuring out which to claim
    for to_parse in match_data: #md=tuple
        # iterate the 'month': [indexes]
        for to_parse_as, indexes in keyword_indexes.items():
            # iterate the [1, 2, 3] indexes
            for index in indexes:
                if index < last_bottom_check and index not in claimed_indexes:
                    last_bottom_check, last_bottom_parser = index, to_parse_as

        claimed_indexes.append(last_bottom_check)
        order_of_operations.append(last_bottom_parser)
        # use last_bottom_check
        # print(last_bottom_check)
        last_bottom_check = 99999
        last_bottom_parser = ""

    return_data = {}
    for kword, data in zip(order_of_operations, match_data):
        fn_return = keywords[kword](data)
        return_data[kword] = fn_return

    if normalize:
        np = list(return_data.values())
        return "{}/{}/{}".format(np[0], np[1], np[2])
    else:
        return return_data

def parse_month(data):
    month_name_indexes = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Feb": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }
    if data in month_name_indexes.keys():
        return month_name_indexes[data]
    return int(data)

def parse_day(data):
    return int(data)

def parse_year(data):
    return int(data)


# d = parse("month-day-year", "May-6-2001")
# print(d)
