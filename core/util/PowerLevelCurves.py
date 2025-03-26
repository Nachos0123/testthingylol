
from core.util.CurveTable             import CurveTable
from core.mappings.HomebaseRating     import HomebaseRating
from core.mappings.SurvivorItemRating import SurvivorItemRating

import json

HomebaseRatingMapping = HomebaseRating
SurvivorItemRating    = SurvivorItemRating

def map_curve_tables(structure):
    return {
        k.lower(): CurveTable(v["Keys"])
        for k, v in structure.items()
    }

PowerLevelCurves = {
    "homebaseRating": CurveTable(HomebaseRatingMapping[0]["ExportValue"]["UIMonsterRating"]["Keys"]),
    "survivorItemRating": map_curve_tables(SurvivorItemRating[0]["ExportValue"])
}