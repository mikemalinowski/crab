import crab
import pymel.core as pm


# ------------------------------------------------------------------------------
class CodeExecutionBehaviour(crab.Behaviour):
    identifier = "Execute Code"
    version = 1

    tooltip = dict(
        code="Python code to evaluate. This will evaluate using eval(your_code)"
    )

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(CodeExecutionBehaviour, self).__init__(*args, **kwargs)

        self.options.code = ""

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def apply(self):

        eval(self.options.code)

        return True
