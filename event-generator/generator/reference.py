"""Reference data: ports, airports, lanes, carriers and shippers.

Everything is fictional apart from the UN/LOCODE port codes and IATA airport codes.
Prices are illustrative only.
"""

OCEAN_PORTS = {
    "CNSHA": ("Shanghai", "CN"),
    "CNNGB": ("Ningbo", "CN"),
    "CNYTN": ("Yantian", "CN"),
    "SGSIN": ("Singapore", "SG"),
    "KRPUS": ("Busan", "KR"),
    "NLRTM": ("Rotterdam", "NL"),
    "DEHAM": ("Hamburg", "DE"),
    "BEANR": ("Antwerp", "BE"),
    "GBFXT": ("Felixstowe", "GB"),
    "ITGOA": ("Genoa", "IT"),
    "USLAX": ("Los Angeles", "US"),
    "USLGB": ("Long Beach", "US"),
    "USNYC": ("New York", "US"),
    "USHOU": ("Houston", "US"),
}

AIRPORTS = {
    "PVG": ("Shanghai Pudong", "CN"),
    "HKG": ("Hong Kong", "HK"),
    "SIN": ("Singapore Changi", "SG"),
    "ICN": ("Seoul Incheon", "KR"),
    "DXB": ("Dubai", "AE"),
    "FRA": ("Frankfurt", "DE"),
    "AMS": ("Amsterdam", "NL"),
    "LHR": ("London Heathrow", "GB"),
    "ORD": ("Chicago O'Hare", "US"),
    "LAX": ("Los Angeles", "US"),
    "JFK": ("New York JFK", "US"),
}

# (origin, destination, trade lane, base USD per 40ft container, transit days)
OCEAN_LANES = [
    ("CNSHA", "NLRTM", "Asia-North Europe", 2400, 32),
    ("CNNGB", "DEHAM", "Asia-North Europe", 2350, 34),
    ("SGSIN", "BEANR", "Asia-North Europe", 2200, 26),
    ("CNSHA", "ITGOA", "Asia-Mediterranean", 2600, 30),
    ("CNYTN", "USLAX", "Transpacific", 2100, 16),
    ("KRPUS", "USLGB", "Transpacific", 1900, 13),
    ("CNSHA", "USNYC", "Asia-US East Coast", 3200, 34),
    ("DEHAM", "USNYC", "Transatlantic", 1800, 11),
    ("NLRTM", "USHOU", "Transatlantic", 1900, 17),
    ("GBFXT", "CNSHA", "North Europe-Asia", 600, 30),
]

# (origin, destination, trade lane, base USD per kg, transit hours)
AIR_LANES = [
    ("PVG", "FRA", "Asia-Europe", 3.4, 13),
    ("HKG", "AMS", "Asia-Europe", 3.6, 14),
    ("SIN", "LHR", "Asia-Europe", 3.1, 15),
    ("ICN", "FRA", "Asia-Europe", 3.3, 13),
    ("PVG", "ORD", "Transpacific", 4.8, 14),
    ("HKG", "LAX", "Transpacific", 4.2, 13),
    ("FRA", "JFK", "Transatlantic", 2.2, 9),
    ("DXB", "FRA", "Middle East-Europe", 2.0, 7),
]

# (code, name, price premium, on-time reliability between 0 and 1)
OCEAN_CARRIERS = [
    ("NWL", "Northwind Lines", 1.00, 0.70),
    ("BLC", "Blue Crest Shipping", 0.95, 0.55),
    ("HRZ", "Horizon Container Line", 1.08, 0.85),
    ("ATL", "Atlas Ocean", 0.92, 0.45),
    ("KST", "Kestrel Maritime", 1.02, 0.65),
    ("ORS", "Orion Sea Freight", 0.98, 0.60),
]

AIRLINES = [
    ("SKY", "Skybridge Cargo", 1.00, 0.88),
    ("AQL", "Aquila Air Freight", 0.94, 0.75),
    ("MER", "Meridian Air Cargo", 1.10, 0.93),
    ("FAL", "Falcon Cargo", 0.90, 0.70),
]

# Equipment multiplier against the 40ft price
EQUIPMENT = {"20DC": 0.55, "40DC": 1.00, "40HC": 1.05}

# Air weight break multiplier against the +500 kg price
WEIGHT_BREAKS = {"+100": 1.15, "+500": 1.00, "+1000": 0.90}

# (id, name, focus, modes, daily bookings)
# focus decides how the shipper picks carriers: cost, reliability or balanced.
SHIPPERS = [
    ("SHP01", "Alpine Outdoor", "cost", ("OCEAN",), 6),
    ("SHP02", "Nordic Home", "reliability", ("OCEAN",), 5),
    ("SHP03", "Brightwave Electronics", "reliability", ("AIR",), 6),
    ("SHP04", "Greenleaf Foods", "balanced", ("OCEAN",), 5),
    ("SHP05", "Vertex Auto Parts", "balanced", ("OCEAN", "AIR"), 6),
    ("SHP06", "Coastline Fashion", "cost", ("OCEAN", "AIR"), 5),
    ("SHP07", "Helix Pharma", "reliability", ("AIR",), 4),
]

VESSEL_NAMES = [
    "Northern Star", "Silver Tide", "Coral Bay", "Iron Gull", "Cape Horizon",
    "Amber Wave", "Polar Drift", "Granite Bay", "Sea Lantern", "Storm Petrel",
]
