from argparse import ArgumentParser

_INCOME_THRESHOLD = 85_528


def calculate_base_tax(income):
    if income > _INCOME_THRESHOLD:
        # normal rate for up to _INCOME_THRESHOLD
        # and %32 for the remaining
        return (
            calculate_base_tax(_INCOME_THRESHOLD)
            + (income - _INCOME_THRESHOLD) * 32 / 100
        )
    else:
        return (income * 17) / 100


def calculate_tax_reducer(income):
    if income < 8_000:
        return 1420
    elif income < 13_000:
        return (871.70 / 5_000) * (income - 8_000)
    elif income < _INCOME_THRESHOLD:
        return 548.30
    elif income < 127_000:
        return (548.30 / 41_472) * (income - 85_582)
    else:
        return 0


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "annual_income", type=int, help="Annual income in zlotys"
    )

    options = parser.parse_args()

    base_tax = calculate_base_tax(options.annual_income)
    reducer = calculate_tax_reducer(options.annual_income)
    total_tax = base_tax - reducer
    net_annual_income = options.annual_income - total_tax

    print("Base Tax:", base_tax, "zl")
    print("Tax Reducer:", reducer, "zl")
    print("Total Tax:", total_tax, "zl")
    print("-" * 30)
    print("Net annual income: ", net_annual_income, "zl")
    print(
        "Net monthly income:",
        net_annual_income / 12,
        "zl",
        f"(taxed @ {total_tax/12} zl per month)",
    )


if __name__ == "__main__":
    main()
