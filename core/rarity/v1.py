import os

class v1:
    def __init__(self):
        self.current_dir = os.path.dirname(__file__)

        self.rarity_backgroundsV1 = {
            "Common": os.path.join(self.current_dir, "images", "rarities", "commun.png"),
            "Uncommon": os.path.join(self.current_dir, "images", "rarities", "uncommon.png"),
            "Rare": os.path.join(self.current_dir, "images", "rarities", "rare.png"),
            "Epic": os.path.join(self.current_dir, "images", "rarities", "epic.png"),
            "Legendary": os.path.join(self.current_dir, "images", "rarities", "legendary.png"),
            "Mythic": os.path.join(self.current_dir, "images", "rarities", "mythic.png"),
            "Icon Series": os.path.join(self.current_dir, "images", "rarities", "icon.png"),
            "DARK SERIES": os.path.join(self.current_dir, "images", "rarities", "dark.png"),
            "Star Wars Series": os.path.join(self.current_dir, "images", "rarities", "starwars.png"),
            "MARVEL SERIES": os.path.join(self.current_dir, "images", "rarities", "marvel.png"),
            "DC SERIES": os.path.join(self.current_dir, "images", "rarities", "dc.png"),
            "Gaming Legends Series": os.path.join(self.current_dir, "images", "rarities", "gaming.png"),
            "Shadow Series": os.path.join(self.current_dir, "images", "rarities", "shadow.png"),
            "Slurp Series": os.path.join(self.current_dir, "images", "rarities", "slurp.png"),
            "Lava Series": os.path.join(self.current_dir, "images", "rarities", "lava.png"),
            "Frozen Series": os.path.join(self.current_dir, "images", "rarities", "frozen.png")
        }

rarities = v1()