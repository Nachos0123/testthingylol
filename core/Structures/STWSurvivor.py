from core.util.PowerLevelCurves  import PowerLevelCurves

class STWSurvivor:
    def __init__(self, data):
        self.template_id = data["templateId"]

        parsed_survivor = self.parse_STW_survivor_template_id()

        self.type = parsed_survivor["type"]
        self.leader = self.type == "manager"

        self.name = parsed_survivor["name"]
        self.tier = parsed_survivor["tier"]
        self.rarity = parsed_survivor["rarity"]

        self.manager_synergy = data["attributes"].get("managerSynergy")
        self.level = data["attributes"].get("level")

        squad_id = data["attributes"].get("squad_id")
        self.squad = {
            "id": squad_id,
            "name": squad_id.split("_")[3],
            "type": squad_id.split("_")[2],
            "slotIdx": data["attributes"].get("squad_slot_idx"),
        } if squad_id else None

        self.personality = data["attributes"].get("personality")

        self.power_level = self.calculate_power_level()
        self.lead_bonus = self.get_lead_bonus()

    def parse_STW_survivor_template_id(self):
        id_parts = self.template_id.split(":")[1].split("_")

        raw_type = id_parts.pop(0)
        if raw_type == "worker":
            type_ = "special"
        elif "manager" in raw_type:
            type_ = "manager"
        else:
            type_ = "basic"

        tier = int(id_parts.pop()[-1])
        rarity = id_parts.pop(0) if type_ == "manager" else id_parts.pop()
        name = "_".join(id_parts) if id_parts else None

        return {"type": type_, "tier": tier, "rarity": rarity, "name": name}

    def calculate_power_level(self):
        key = f"manager_{self.rarity}_t0{self.tier}" if self.leader else f"default_{self.rarity}_t0{self.tier}"
        return PowerLevelCurves['survivorItemRating'][key].eval(self.level)

    def get_lead_bonus(self):
        if not self.manager_synergy or not self.squad:
            return 0

        STW_LEAD_SYNERGY = {
            "trainingteam": "IsTrainer",
            "fireteamalpha": "IsSoldier",
            "closeassaultsquad": "IsMartialArtist",
            "thethinktank": "IsInventor",
            "emtsquad": "IsDoctor",
            "corpsofengineering": "IsEngineer",
            "scoutingparty": "IsExplorer",
            "gadgeteers": "IsGadgeteer",
        }

        leader_match = self.manager_synergy.split(".")[2]
        return self.power_level if STW_LEAD_SYNERGY.get(self.squad["name"]) == leader_match else 0

    def calc_survivor_bonus(self, leader):
        if self.leader or not leader.leader:
            return 0

        if self.personality == leader.personality:
            return {"sr": 8, "vr": 5, "r": 4, "uc": 3, "c": 2}.get(leader.rarity, 0)

        return -2 if leader.rarity == "sr" and self.power_level > 2 else 0