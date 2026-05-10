# A list of US states for the dropdown
US_STATES = [
    "", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
]

# Simplified risk score based on spec citation [cite: 104]
LANDLORD_FLEXIBILITY_RISK = {
    "Texas": "Low Risk (e.g., 21-28 days eviction)",
    "Indiana": "Low Risk",
    "Alabama": "Low Risk",
    "New Jersey": "High Risk (e.g., long uncontested eviction durations)",
    "California": "High Risk (e.g., long uncontested eviction durations)",
    # This can be expanded with more research
}

# Rehab costs per square foot based on spec [cite: 96, 97, 98]
REHAB_COSTS_PER_SQFT = {
    "None": 0,
    "Light (Cosmetic/Paint)": 20,  # Using average of $15-$25
    "Medium (Systems/Plumbing)": 37.5, # Using average of $25-$50
    "Heavy (Gut/Studs)": 65,
}

ASSET_TYPE_OPTIONS = ['Single-Family', 'Condo', 'Townhome', '2-Unit', '4-Unit', 'Commercial Multifamily']
MARKET_PHASE_OPTIONS = ['Recovery', 'Expansion', 'Hyper-Supply', 'Recession']
