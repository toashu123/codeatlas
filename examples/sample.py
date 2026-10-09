class Calculator:

    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b


def main():
    calculator = Calculator()
    result = calculator.add(10, 20)
    print(result)


main()
