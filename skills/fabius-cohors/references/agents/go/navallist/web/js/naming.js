// naming.js - Random Trip Name Generator

const ADJECTIVES = [
    "Salty", "Blue", "Calm", "Misty", "Sunny", "Windy", "Royal", "Azure", "Brave", "Jolly", 
    "Happy", "Lucky", "Magic", "Wild", "Gold", "Bold", "Swift", "Fair", "Free", "Grey", 
    "Deep", "Red", "Hot", "Cool", "Nice", "Grand", "Tidal", "Dock"
];

const NOUNS = [
    "Crab", "Whale", "Shark", "Crew", "Mate", "Helm", "Wheel", "Sail", "Mast", "Deck", 
    "Hull", "Keel", "Boat", "Ship", "Yacht", "Raft", "Ferry", "Tug", "Barge", "Sloop", 
    "Ketch", "Skiff", "Wave", "Tide", "Surge", "Swell", "Foam", "Spray", "Mist", "Fog", 
    "Rain", "Wind", "Gale", "Storm", "Moon", "Star", "Sky", "Sun", "Ray", "Beam", 
    "Light", "Night", "Day", "Dawn", "Dusk", "Bay", "Cove", "Inlet", "Sound", "Fiord", 
    "Gulf", "Delta", "River", "Lake", "Pond", "Pool", "Well", "Eddy", "Deep", "Shoal", 
    "Reef", "Bank", "Bar", "Sand", "Beach", "Shore", "Coast", "Land", "Isle", "Key", 
    "Cay", "Atoll", "Cape", "Point", "Rock", "Stone", "Shell", "Coral", "Pearl", "Map", 
    "Chart", "Log", "Book", "Flag"
];

export function generateTripName() {
    const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)];
    const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)];
    const num = Math.floor(Math.random() * 100) + 1; // 1-100
    
    // Format: AdjectiveNounNum (e.g., SaltyCrab42)
    return `${adj}${noun}${num}`;
}
