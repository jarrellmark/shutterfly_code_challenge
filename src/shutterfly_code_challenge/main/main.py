from events import BaseEvent
from events import CustomerEvent
from events import ImageUploadEvent
from events import OrderEvent
from events import SiteVisitEvent

from datetime import datetime, timedelta
import operator
import pprint
import time

def Ingest(e, D):
    if isinstance(e, dict):
        if 'type' in e:
            event = None

            if e['type'] == 'CUSTOMER':
                event = CustomerEvent(e)
            elif e['type'] == 'SITE_VISIT':
                event = SiteVisitEvent(e)
            elif e['type'] == 'IMAGE_UPLOAD':
                event = ImageUploadEvent(e)
            elif e['type'] == 'ORDER':
                event = OrderEvent(e)

            if not event == None:
                event.merge(D)

"""
Returns the top x customers by Simple LTV in descending order.
"""
def TopXSimpleLTVCustomerEvents(x, D):
    if (isinstance(x, int) or isinstance(x, long)):
        if not D.get('ORDER') == None and len(D['ORDER']) > 0:
            all_customers = set()
            min_date = None
            max_date = None

            for key, attributes in D['ORDER'].items():
                all_customers.add(attributes['customer_id'].value)
                if (min_date == None or attributes['created_time'].value < min_date):
                    min_date = attributes['created_time'].value
                if (max_date == None or attributes['created_time'].value > max_date):
                    max_date = attributes['created_time'].value

            min_week = __startOfWeek(min_date)
            max_week = __startOfWeek(max_date)

            weekly_structure = __generate_weekly_structure(min_week, max_week, all_customers)
            __populate_weekly_structure(weekly_structure, D['ORDER'])
            customer_ltvs = __generate_customer_ltvs(weekly_structure)

            return __top_x_ltvs(x, customer_ltvs)

    return []


def __startOfWeek(date):
    current_date = date

    # While index is not Sunday
    while current_date.weekday() != 6:
        current_date = current_date - timedelta(days=1)

    return current_date.date()

"""
Looks like:
  {
    '2016-52': {
      'customer_id_1': {
        num_orders: 0,
        week_average: 0
      },
      'customer_id_2': {
        num_orders: 0,
        week_average: 0
      }
    },
    '2017-01': {
      'customer_id_1': {
        num_orders: 0,
        week_average: 0
      },
      'customer_id_2': {
        num_orders: 0,
        week_average: 0
      }
    }
  }
"""
def __generate_weekly_structure(min_week, max_week, customers):
    weekly_structure = {}
    current_week = min_week

    while current_week <= max_week:
        week_structure = {}
        for customer in customers:
            week_structure[customer] = {
                'num_orders': 0,
                'week_average': 0
            }
        weekly_structure[current_week] = week_structure

        current_week = current_week + timedelta(weeks=1)

    return weekly_structure

"""
Fills weekly_structure's num_orders and week_average.
"""
def __populate_weekly_structure(weekly_structure, orders):
    for order_key, order_attributes in orders.items():
        if not order_attributes.get('created_time') == None:
            order_week = __startOfWeek(order_attributes['created_time'].value)
            customer_structure = weekly_structure[order_week][order_attributes['customer_id'].value]

            num_orders = customer_structure['num_orders']
            week_average = customer_structure['week_average']
            total_amount = order_attributes['total_amount'].value

            customer_structure['week_average'] = (num_orders * week_average + total_amount) / (num_orders + 1)
            customer_structure['num_orders'] += 1

            weekly_structure[order_week][order_attributes['customer_id'].value] = customer_structure

"""
Calculates ltv (52(a) * 10) for each customer

Looks like:
  {
    'customer_1': 80,
    'customer_2': 85
  }
"""
def __generate_customer_ltvs(weekly_structure):
    """
    First calculate total of weekly averages for each customer.
    """
    customer_totals = {}

    for week, customers in weekly_structure.items():
        for customer, values in customers.items():
            if customer_totals.get(customer) == None:
                customer_totals[customer] = values['week_average']
            else:
                customer_totals[customer] += values['week_average']

    """
    Now calculate average customer value per week for each customer.
    """
    customer_averages = customer_totals
    customer_totals = None

    for customer, total in customer_averages.items():
        customer_averages[customer] = total / len(weekly_structure)

    """
    Now calculate LTVs.
    """
    customer_ltvs = customer_averages
    customer_averages = None

    for customer, average in customer_ltvs.items():
        customer_ltvs[customer] = 52 * average * 10

    return customer_ltvs

"""
As long as x is small, this is O(len(customer_ltvs)).
"""
def __top_x_ltvs(x, customer_ltvs):
    min_ltv = None
    min_customer = None
    top_dict = {}

    for customer, ltv in customer_ltvs.items():
        # check if should add customer
        if (min_ltv == None or len(top_dict) < x or ltv > min_ltv):
            # remove smallest customer in top_dict
            if len(top_dict) == x:
                del top_dict[min_customer]
            # add customer
            top_dict[customer] = ltv
            # (re)calculate min_ltv and min_customer
            if min_ltv == None:
                min_ltv = ltv
                min_customer = customer
            else:
                for c, l in top_dict.items():
                    if l < min_ltv:
                        min_ltv = l
                        min_customer = c

    top_dict_sorted = sorted(top_dict.items(), key=operator.itemgetter(1), reverse=True)
    top_dict_sorted_formatted = [{'customer_id': item[0], 'simple_ltv': item[1]} for item in top_dict_sorted]

    return top_dict_sorted_formatted
