class Combat:
    def __init__(self, active=False):
        active = active

    def __str__(self):
        data = {
            key if not key.startswith("_") else None: val
            for key, val in self.__dict__.items()
        }
        return str(data)
