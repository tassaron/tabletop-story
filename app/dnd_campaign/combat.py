class Combat:
    def __init__(self, scene_id=0, active=False):
        self.scene_id = int(scene_id)
        self.active = active

    def __str__(self):
        data = {
            key if not key.startswith("_") else None: val
            for key, val in self.__dict__.items()
        }
        return str(data)
