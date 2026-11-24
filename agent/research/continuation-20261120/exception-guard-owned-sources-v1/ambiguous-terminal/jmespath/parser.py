class Parser:
    def _do_parse(self, expression):
        try:
            return helper(expression)
        except first.Error:
            raise
        except second.Error:
            raise
