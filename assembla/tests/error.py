from ..error import AssemblaError

class TestForAssemblaError(object):
    # General usage tests.

    def test_assembla_error_can_be_raised(self):
        try:
            raise AssemblaError(100)
        except TypeError:
            raise Exception('Should not get here.')
        except AssemblaError:
            pass

    def test_assembla_error_reports_message_correctly(self):
        try:
            raise AssemblaError(100)
        except AssemblaError as e:
            assert str(e) == AssemblaError.error_codes[100]