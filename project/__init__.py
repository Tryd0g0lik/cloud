class Csrft:
    """
    Class Csrft() it is analogous for the 'useState()' from react.
    Here is a task  - create the 'csrftoken' and compare the this 'csrftoken' \
    with 'csrftoken' from the request.
    First, we need to get the 'csrftoken' from the cenerator.
    Then we will be compare the 'csrftoken' (backend's version) with \
     the 'csrftoken' (vertion of client) from the request.
    :param state: the state of`'csrftoken'.
    :param set_state: For a set the `'csrftoken' from  csrf-token's generator.
    """

    # pass
    def __init__(self):
        self.state = ""

    def set_state(self, view):
        self.state = view


use_CSRFToken = Csrft()
