import math
import numpy as np

def simple_return(buy_price, sell_price):
    return -buy_price + sell_price

def simple_rate_of_return(buy_price, sell_price):
    return simple_return(buy_price, sell_price) / buy_price

def present_value(future_cash, rate_of_return, periods):
    return future_cash / (1 + rate_of_return)**periods


def net_present_value_single(initial_investment, future_cash, discount_rate, periods):
    return (future_cash / (1 + discount_rate)**periods) - initial_investment

# Discount rate is the return rate that could be earned in alternative investments.
# If the alternative investment is doing nothing, then the discount rate is the inflation rate.
def net_present_value_multiple(initial_investment, future_cash, discount_rate, periods):
    return -initial_investment + future_cash

def set_probability(probability_up, probability_down):
    return np.array([probability_up, probability_down])

# This is only true if probability_up + probability_down = 1.0
def calc_probability_down(probability_up):
    return 1 - probability_up

def set_uncertein_sell_price(sell_price_up, sell_price_down):
    return np.array([sell_price_up, sell_price_down])

# The expectation is the dot product between probability and sell price
# expectation = (probability_up * sell_price_up) + (probability_down * sell_price_down)
def expectation(probability, sell_price):
    return np.dot(probability, sell_price)

def expected_return(buy_price, probability, sell_price):
    simple_return = np.array([sell_price[0] - buy_price, sell_price[1] - buy_price])
    return np.dot(probability, simple_return)

def expected_rate_of_return(buy_price, probability, sell_price):
    return expected_return(buy_price, probability, sell_price) / buy_price

def variance(buy_price, probability, sell_price):
    uncertein_simple_rate_of_return = np.array([simple_rate_of_return(buy_price, sell_price[0]),
                                                simple_rate_of_return(buy_price, sell_price[1])])
    mu = expected_rate_of_return(buy_price, probability, sell_price)
    deviation = (uncertein_simple_rate_of_return - mu) ** 2
    return np.dot(probability, deviation)

# Volatility is standard deviation of the expected rate of return
# Which is square root of variance
def volatility(varian):
    return math.sqrt(varian)

# Calculate the compounded interest after a timeframe of x time units
# periods = how many times the interest is compounded during timeframe
def compound_interest(starting_investment, interest_rate, time_span, periods):
        return starting_investment * (1 + (interest_rate / periods))**(periods * time_span)

# Calculate if the stock price is going up or down or staying the same by 1%
# The method calculates the probability by counting all the times stock price 
# went up, down, or remained the same. 
# The treshold is 1%. If the price changes by 1% or more the stock goes up or down.
# If the price changes by less than 1% the stock stays the same.
def calculate_stock_probabilities(stock_prices):
    up_count = 0
    down_count = 0
    no_movement_count = 0

    for i in range(1, len(stock_prices)):
        price_difference = (stock_prices[i] - stock_prices[i - 1]) / stock_prices[i - 1] * 100
        if abs(price_difference) >= 1.0:
            if price_difference > 0:
                up_count += 1
            else:
                down_count += 1
        else:
            no_movement_count += 1

    total_days = len(stock_prices) - 1
    probability_up = up_count / total_days
    probability_down = down_count / total_days
    probability_no_movement = no_movement_count / total_days

    # Ensure that probability_up + probability_down + probability_no_movement = 1.0
    total_probability = probability_up + probability_down + probability_no_movement
    if total_probability != 1.0:
        probability_no_movement += 1.0 - total_probability

    return [probability_up, probability_down, probability_no_movement]

if __name__ == "__main__":
    buy_price = 10
    probability = set_probability(0.3, 0.7)
    future_sell_prices = set_uncertein_sell_price(30, 20)
    var = variance(buy_price, probability, future_sell_prices)
    print(var)