class Parser:
    def _do_parse(self, expression):
        try:
            return helper(expression)
        except factory().Error:
            raise
