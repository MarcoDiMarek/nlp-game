import pprint

class Collider:
    """Template class to be inherited by specific types of colliders.
       
       Game objects that have their own colliders can collide with each other.
       
       Relative Locaion to Object = (0,0) center (pivot) of the object"""

    def __init__(self, RelativeLocToObject, active=False):
        self.location = (0,0) # 0,0 center of the object
        self.active = active
    pass

class BoxCollider(Collider):
    def __init__(self, RelativeLocToObject, RelativeSizeToObject):
        super().__init__(self, RelativeLocToObject)
        self.boundaries = (
                        # Top Left
                        (RelativeLocToObject[0]-RelativeSizeToObject[0]/2, 
                        RelativeLocToObject[1]-RelativeSizeToObject[1]/2),
                        # Top Rigth
                        (RelativeLocToObject[0]+RelativeSizeToObject[0]/2, 
                        RelativeLocToObject[1]-RelativeSizeToObject[1]/2),
                        # Bottom Left
                        (RelativeLocToObject[0]-RelativeSizeToObject[0]/2, 
                        RelativeLocToObject[1]+RelativeSizeToObject[1]/2),
                        # Bottom Right
                        (RelativeLocToObject[0]+RelativeSizeToObject[0]/2, 
                        RelativeLocToObject[1]+RelativeSizeToObject[1]/2)
                    )
    def __str__(self) -> str:
        boundaries = zip(("Top Left", "Top Right", "Bottom Left", "Bottom Right"), self.boundaries)
        return pprint.pformat(list(boundaries))



#Example
collider = BoxCollider((0,0),(1,1))
print(collider)