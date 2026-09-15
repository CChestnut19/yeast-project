"""The 27 Supplementary Note 9 panels and source layout from the supplied archive."""

from dataclasses import dataclass

@dataclass(frozen=True)
class Panel:
    panel_id: str
    page: int
    order: int
    construct: str
    dbd: str
    operator: str
    lbd: str
    inducer: str
    source_kind: str
    block_row: int
    dose_unit: str


PANELS = [
    Panel("SN9-P1-A", 1, 1, "lexAbs94-RpaR179", "LexAbs94", "lexObs", "RpaR179", "pC-HSL", "DBD", 145, "uM"),
    Panel("SN9-P1-B", 1, 2, "lexAxa101-RpaR179", "LexAxa101", "lexOxa", "RpaR179", "pC-HSL", "DBD", 34, "uM"),
    Panel("SN9-P1-C", 1, 3, "lexAmm115-RpaR179", "LexAmm115", "lexOmm", "RpaR179", "pC-HSL", "DBD", 12, "uM"),
    Panel("SN9-P1-D", 1, 4, "lexAec87-RpaR179", "LexAec87", "lexOrec.sym", "RpaR179", "pC-HSL", "DBD", 23, "uM"),
    Panel("SN9-P2-A", 2, 1, "lexAfs104-RpaR179", "LexAfs104", "lexOfs", "RpaR179", "pC-HSL", "DBD", 123, "uM"),
    Panel("SN9-P2-B", 2, 2, "lexAgs91-RpaR179", "LexAgs91", "lexOgs", "RpaR179", "pC-HSL", "DBD", 134, "uM"),
    Panel("SN9-P2-C", 2, 3, "HKCI84-RpaR179", "HKCI84", "OHKCI", "RpaR179", "pC-HSL", "DBD", 45, "uM"),
    Panel("SN9-P2-D", 2, 4, "DeoR92-RpaR179", "DeoR92", "ODeoR", "RpaR179", "pC-HSL", "DBD", 101, "uM"),
    Panel("SN9-P2-E", 2, 5, "PurR60-RpaR179", "PurR60", "purO", "RpaR179", "pC-HSL", "DBD", 112, "uM"),
    Panel("SN9-P3-A", 3, 1, "CI43470-RpaR179", "CI43470", "OCI434", "RpaR179", "pC-HSL", "DBD", 1, "uM"),
    Panel("SN9-P3-B", 3, 2, "CI94-OL1-RpaR179", "CI94-OL1", "OCI OL1", "RpaR179", "pC-HSL", "DBD", 57, "uM"),
    Panel("SN9-P3-C", 3, 3, "CI94-OR1-RpaR179", "CI94-OR1", "OCI OR1", "RpaR179", "pC-HSL", "DBD", 68, "uM"),
    Panel("SN9-P3-D", 3, 4, "CI94-Osym-RpaR179", "CI94-Osym", "OCI Osym", "RpaR179", "pC-HSL", "DBD", 79, "uM"),
    Panel("SN9-P3-E", 3, 5, "RecApact104-RpaR179", "RecApact104", "ORecApact", "RpaR179", "pC-HSL", "DBD", 90, "uM"),
    Panel("SN9-P4-A", 4, 1, "lexAbs94-LasR177", "LexAbs94", "lexObs", "LasR177", "3OC12-HSL", "LBD", 208, "nM"),
    Panel("SN9-P4-B", 4, 2, "lexAbs94-BjaR180", "LexAbs94", "lexObs", "BjaR180", "IV-HSL", "LBD", 228, "uM"),
    Panel("SN9-P4-C", 4, 3, "lexAbs94-CinR179", "LexAbs94", "lexObs", "CinR179", "3OHC14-HSL", "LBD", 218, "nM"),
    Panel("SN9-P4-D", 4, 4, "lexAbs94-TraR174", "LexAbs94", "lexObs", "TraR174", "3OC8-HSL", "LBD", 238, "uM"),
    Panel("SN9-P5-A", 5, 1, "lexAbs94-ER282-595", "LexAbs94", "lexObs", "ER282-595", "beta-estradiol", "LBD", 157, "nM"),
    Panel("SN9-P5-B", 5, 2, "lexAbs94-DHBR282-595", "LexAbs94", "lexObs", "DHBR282-595", "DHB", "LBD", 167, "uM"),
    Panel("SN9-P5-C", 5, 3, "lexAbs94-PR", "LexAbs94", "lexObs", "PR", "RU486", "LBD", 177, "uM"),
    Panel("SN9-P5-D", 5, 4, "lexAbs94-GR487-777", "LexAbs94", "lexObs", "GR487-777", "dexamethasone", "LBD", 198, "uM"),
    Panel("SN9-P5-E", 5, 5, "lexAbs94-MR669-984", "LexAbs94", "lexObs", "MR669-984", "aldosterone", "LBD", 187, "uM"),
    Panel("SN9-P6-A", 6, 1, "lexAec87-CarRecc169", "LexAec87", "lexOrec.sym", "CarRecc169", "3OC6-HSL", "CAR_SPECIAL", 285, "uM"),
    Panel("SN9-P6-B", 6, 2, "lexAbs94-acVHH", "LexAbs94", "lexObs", "acVHH", "caffeine", "LBD", 248, "nM"),
    Panel("SN9-P6-C", 6, 3, "CI94-Osym-SmaR179", "CI94-Osym", "OCI Osym", "SmaR179", "C4-HSL", "LBD", 258, "nM"),
    Panel("SN9-P6-D", 6, 4, "PurR60-BjaR180S107R", "PurR60", "purO", "BjaR180S107R", "IV-HSL", "BJAMUT_SPECIAL", 273, "uM"),
]
