from thecurator.transformation import NamedTransformer, output


class AdditionTransformer(NamedTransformer):
    def one(self):
        return 1

    def two(self):
        return 2

    @output
    def plus_one(self, row):
        return row['value'] + self.one()

    @output
    def plus_two(self, row):
        return row['value'] + self.two()


class TestItWorks():
    def test_works(self):
        result = AdditionTransformer().transform({'value': 1})
        assert result == {'plus_one': 2, 'plus_two': 3}
