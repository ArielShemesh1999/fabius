// Static definition of the Checklist structure
// Generated from checklist.yaml - DO NOT EDIT MANUALLY

const CHECKLIST_SCHEMA = {
    "Boat Information": [
            {
                "id": "boat_name",
                "label": "Name",
                "type": "text",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "The official name of the vessel as displayed on the hull.",
                "explanation_returning": "Confirm the vessel name for the logbook entry."
            },
            {
                "id": "marina",
                "label": "Marina",
                "type": "text",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "The name of the marina where the boat is currently docked.",
                "explanation_returning": "The name of the marina where you are returning."
            },
            {
                "id": "slip",
                "label": "Slip",
                "type": "text",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "The specific slip or dock number where the boat is located.",
                "explanation_returning": "The specific slip or dock number where you are docking."
            }
        ],
    "Electrical Systems": [
            {
                "id": "shore_power",
                "label": "Shore Power",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check that the shore power connection is active and charging the batteries.",
                "explanation_returning": "Connect shore power and verify batteries are charging."
            },
            {
                "id": "shore_power_cable",
                "label": "Shore Power Cable",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Inspect the cable for any fraying, burns, or loose connections at both ends.",
                "explanation_returning": "Coil the shore power cable neatly if not in use, or check connections if plugged in."
            },
            {
                "id": "generator",
                "label": "Generator",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Start the generator and verify it provides stable AC power to the vessel.",
                "explanation_returning": "Ensure the generator is turned off and cooling water seacock is closed if required."
            },
            {
                "id": "battery",
                "label": "Battery",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check battery voltage levels and ensure terminals are clean and tight.",
                "explanation_returning": "Turn off house and engine battery switches if leaving the boat."
            },
            {
                "id": "outlets",
                "label": "Outlets",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Verify that GFCI and standard outlets have power when on shore power or inverter.",
                "explanation_returning": "Unplug unnecessary devices from outlets."
            },
            {
                "id": "inverter",
                "label": "Inverter",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Test the inverter by powering a small AC device while disconnected from shore power.",
                "explanation_returning": "Ensure the inverter is turned off."
            }
        ],
    "Lights": [
            {
                "id": "nav_lights",
                "label": "Navigation Lights",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Verify that red (port), green (starboard), and white (stern) lights are functional for night operations.",
                "explanation_returning": "Ensure all navigation lights are turned off."
            },
            {
                "id": "steaming_lights",
                "label": "Steaming Lights",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check the forward-facing white light on the mast used when under engine power.",
                "explanation_returning": "Ensure steaming lights are off."
            },
            {
                "id": "deck_light",
                "label": "Deck Light",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check the spreader or mast-mounted lights used for illuminating the deck at night.",
                "explanation_returning": "Ensure deck lights are off."
            },
            {
                "id": "cabin_lights",
                "label": "Cabin Lights",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Ensure all interior lighting is functional, including red 'night' lights if equipped.",
                "explanation_returning": "Turn off all cabin lights."
            }
        ],
    "Comms": [
            {
                "id": "nav_systems",
                "label": "Navigation Systems",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Ensure GPS, Chartplotter, and Depth Sounder power on and acquire a signal.",
                "explanation_returning": "Turn off GPS, Chartplotter, and other navigation electronics."
            },
            {
                "id": "radio",
                "label": "Radio",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Perform a radio check on VHF Channel 16/9 to ensure transmission and reception are clear.",
                "explanation_returning": "Turn off the VHF radio."
            }
        ],
    "Paperwork": [
            {
                "id": "rental_agreement",
                "label": "Rental Agreement",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Ensure a signed copy of the rental or charter agreement is on board.",
                "explanation_returning": "Ensure the rental agreement is ready for return processing."
            },
            {
                "id": "boat_documentation",
                "label": "Boat Documentation",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Verify that the vessel's registration or USCG documentation is current and accessible.",
                "explanation_returning": "Return documentation to its designated folder."
            },
            {
                "id": "vessel_assist",
                "label": "Vessel Assist",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Confirm membership details for SeaTow, BoatUS, or similar towing services.",
                "explanation_returning": "N/A"
            }
        ],
    "Engine": [
            {
                "id": "engine_hours",
                "label": "Engine Hours",
                "type": "number",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Record the current reading from the engine hour meter.",
                "explanation_returning": "N/A"
            },
            {
                "id": "water_exhaust",
                "label": "Exhaust",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "With the engine running, verify that cooling water is being expelled from the exhaust port.",
                "explanation_returning": "N/A"
            },
            {
                "id": "fuel",
                "label": "Fuel",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check the fuel gauge and visually inspect the tank if possible. Ensure sufficient fuel for the trip.",
                "explanation_returning": "Note the fuel level upon return. Refuel if required by charter agreement."
            },
            {
                "id": "belts",
                "label": "Belts",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check the tension and condition of the alternator and water pump belts.",
                "explanation_returning": "N/A"
            },
            {
                "id": "coolant",
                "label": "Coolant",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check the engine coolant level in the expansion tank. ONLY CHECK WHEN ENGINE IS COLD.",
                "explanation_returning": "Check for any coolant leaks in the bilge."
            },
            {
                "id": "oil",
                "label": "Oil",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check the engine oil level using the dipstick. Ensure it is between the min/max marks.",
                "explanation_returning": "N/A"
            }
        ],
    "Safety": [
            {
                "id": "first_aid_kit",
                "label": "First Aid Kit",
                "type": "check",
                "allow_photo": true,
                "allow_multi_photo": false,
                "explanation_departing": "Locate the first aid kit and ensure it is fully stocked and not expired.",
                "explanation_returning": "Report any items used from the First Aid Kit.",
                "picture_reason": "Take a photo of the kit so people can quickly find it in an emergency."
            },
            {
                "id": "extinguishers",
                "label": "Extinguishers",
                "type": "count",
                "allow_photo": true,
                "allow_multi_photo": true,
                "explanation_departing": "Verify the number, location, and charge level (gauge in green) of all fire extinguishers.",
                "explanation_returning": "Verify all extinguishers are still in place.",
                "picture_reason": "Take a photo of the extinguishers so people can quickly find it in an emergency."
            },
            {
                "id": "flares",
                "label": "Flares",
                "type": "count",
                "allow_photo": true,
                "allow_multi_photo": false,
                "explanation_departing": "Check the quantity and expiration dates of all visual distress signals (flares).",
                "explanation_returning": "Verify all flares are accounted for.",
                "picture_reason": "Take a photo of the flares so people can quickly find it in an emergency."
            },
            {
                "id": "pfd",
                "label": "PFD",
                "type": "count",
                "allow_photo": true,
                "allow_multi_photo": false,
                "explanation_departing": "Count all Personal Flotation Devices. Ensure they are the correct size and in good condition.",
                "explanation_returning": "Stow all PFDs in their designated storage areas. Ensure they are dry.",
                "picture_reason": "Take a photo of the PFD storage area to show they are accessible."
            },
            {
                "id": "ring_buoy",
                "label": "Ring Buoy",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Ensure the throwable ring buoy is accessible and the line is not tangled.",
                "explanation_returning": "Ensure the ring buoy is secured."
            },
            {
                "id": "lifesling",
                "label": "Lifesling",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Verify the Lifesling is mounted correctly and the cover is in good condition.",
                "explanation_returning": "Ensure the Lifesling is secured."
            }
        ],
    "Lines/Sheets/Fenders": [
            {
                "id": "docklines",
                "label": "Docklines",
                "type": "count",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Ensure there are enough docklines for the vessel, including spares for heavy weather.",
                "explanation_returning": "Secure the boat with docklines. Use spring lines if necessary."
            },
            {
                "id": "fenders",
                "label": "Fenders",
                "type": "count",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check that fenders are inflated and have appropriate lines for hanging.",
                "explanation_returning": "Deploy fenders on the appropriate side before docking."
            },
            {
                "id": "jack_lines",
                "label": "Jack lines",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check if present and inspect safety jack lines for UV damage or fraying.",
                "explanation_returning": "Remove and stow jack lines if applicable."
            },
            {
                "id": "standing_rigging",
                "label": "Standing Rigging",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Visually inspect shrouds, stays, and turnbuckles for any signs of fatigue or 'meat hooks'.",
                "explanation_returning": "N/A"
            },
            {
                "id": "life_lines",
                "label": "Life Lines",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check the tension and integrity of the lifelines and stanchions.",
                "explanation_returning": "N/A"
            },
            {
                "id": "preventer",
                "label": "Preventer",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check if there is a a boom preventer available for downwind sailing.",
                "explanation_returning": "Stow the preventer."
            }
        ],
    "Inventory": [
            {
                "id": "winch_handles",
                "label": "Winch Handles",
                "type": "count",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Count all winch handles. Ensure at least one is easily reachable from the cockpit.",
                "explanation_returning": "Count and stow all winch handles."
            },
            {
                "id": "air_horn",
                "label": "Air Horn",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Test the air horn to ensure it is loud and has sufficient pressure.",
                "explanation_returning": "N/A"
            },
            {
                "id": "flashlight",
                "label": "Flashlight",
                "type": "check",
                "allow_photo": true,
                "allow_multi_photo": false,
                "explanation_departing": "Verify that all flashlights are functional and have fresh batteries.",
                "explanation_returning": "Stow all flashlights.",
                "picture_reason": "Take a photo so people know where it is in an emergency."
            },
            {
                "id": "toolbox",
                "label": "Toolbox",
                "type": "check",
                "allow_photo": true,
                "allow_multi_photo": false,
                "explanation_departing": "Ensure basic tools (wrenches, screwdrivers, pliers) are on board for minor repairs.",
                "explanation_returning": "Ensure all tools are returned to the toolbox.",
                "picture_reason": "Take a photo so people know where it is in an emergency."
            },
            {
                "id": "boat_hook",
                "label": "Boat Hook",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check that the boat hook is accessible and functions (telescopes) correctly.",
                "explanation_returning": "Use the boat hook for docking if needed, then stow it."
            }
        ],
    "Steering": [
            {
                "id": "wheel_control",
                "label": "Wheel Control",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Turn the wheel from lock to lock to ensure smooth operation of the rudder.",
                "explanation_returning": "Center the wheel and lock it if possible."
            },
            {
                "id": "forward_reverse",
                "label": "Forward/Reverse",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "While teh boat is still secure, test the engine shifter to ensure it engages forward and reverse gears smoothly.",
                "explanation_returning": "Leave the shifter in neutral (or reverse if sailing prop)."
            },
            {
                "id": "emergency_tiller",
                "label": "Emergency Tiller",
                "type": "check",
                "allow_photo": true,
                "allow_multi_photo": false,
                "explanation_departing": "Locate the emergency tiller and ensure you know how to fit it to the rudder post.",
                "explanation_returning": "N/A",
                "picture_reason": "Photo the emergency tiller so it can be found in an emergency."
            }
        ],
    "Water Systems": [
            {
                "id": "manual_bilge",
                "label": "Manual Bilge",
                "type": "check",
                "allow_photo": true,
                "allow_multi_photo": false,
                "explanation_departing": "Test the manual bilge pump to ensure it primes and pumps water.",
                "explanation_returning": "N/A",
                "picture_reason": "Photo the bilge pump handle in its designated storage location."
            },
            {
                "id": "automatic_bilge",
                "label": "Automatic Bilge",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Lift the float switch in the bilge to ensure the automatic pump activates.",
                "explanation_returning": "Ensure the automatic bilge pump switch is set to AUTO."
            },
            {
                "id": "water",
                "label": "Water",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check the level of the fresh water tanks.",
                "explanation_returning": "Refill water tanks if required."
            },
            {
                "id": "water_pressure",
                "label": "Water Pressure",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Turn on the water pressure pump and check all faucets for flow.",
                "explanation_returning": "Turn off the water pressure pump."
            },
            {
                "id": "heads_working",
                "label": "Heads Working",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Flush the marine toilets (heads) to ensure they pump and drain correctly.",
                "explanation_returning": "Ensure heads are pumped dry and seacocks are closed."
            }
        ],
    "Sails": [
            {
                "id": "unfurl_main",
                "label": "Unfurl main",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Partially unfurl the mainsail to check for tears, battens, or jamming.",
                "explanation_returning": "Ensure the mainsail is properly furled or flaked and covered."
            },
            {
                "id": "unfurl_jib",
                "label": "Unfurl jib",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Partially unfurl the jib/genoa to inspect the UV cover and overall condition.",
                "explanation_returning": "Ensure the jib is tightly furled and sheets are secured."
            },
            {
                "id": "check_furl_lock",
                "label": "Check furl lock",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Ensure the furling lines are secured and the locks are functional.",
                "explanation_returning": "Secure all furling lines."
            },
            {
                "id": "check_reefing",
                "label": "Check reefing",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Verify that reefing lines are correctly led and clear of tangles.",
                "explanation_returning": "Slack reefing lines if necessary."
            }
        ],
    "Anchor": [
            {
                "id": "anchor_bow",
                "label": "Anchor Bow",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check that the primary bow anchor is secured and the pin is in place.",
                "explanation_returning": "Ensure the anchor is stowed and secured with the pin."
            },
            {
                "id": "anchor_stern",
                "label": "Anchor Stern",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Verify the secondary or stern anchor is accessible and its rode is clear.",
                "explanation_returning": "Stow the stern anchor and rode."
            },
            {
                "id": "windlass",
                "label": "Windlass",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Test the electric or manual windlass to ensure it can deploy and retrieve the anchor.",
                "explanation_returning": "Turn off the windlass breaker."
            },
            {
                "id": "chain_length",
                "label": "Chain Length",
                "type": "text",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Note the total length of anchor chain available (often marked with paint or zip ties).",
                "explanation_returning": "N/A"
            },
            {
                "id": "rope_length",
                "label": "Rope Length",
                "type": "text",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Note the total length of anchor rope (rode) attached to the chain.",
                "explanation_returning": "N/A"
            }
        ],
    "Food Management": [
            {
                "id": "stove_top",
                "label": "Stove Top",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Test all burners on the stove to ensure they ignite and stay lit.",
                "explanation_returning": "Ensure all burner knobs are off and the solenoid is closed."
            },
            {
                "id": "oven",
                "label": "Oven",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Verify the oven ignites and the thermostat is functional.",
                "explanation_returning": "Ensure the oven is off."
            },
            {
                "id": "grill",
                "label": "Grill",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Check the stern-mounted grill and ensure the propane/gas supply is secure.",
                "explanation_returning": "Clean the grill and turn off the gas supply."
            },
            {
                "id": "refrigerator",
                "label": "Refrigerator",
                "type": "check",
                "allow_photo": false,
                "allow_multi_photo": false,
                "explanation_departing": "Ensure the refrigeration system is cooling and the door seals are tight.",
                "explanation_returning": "Empty the refrigerator and leave the door slightly ajar to prevent mold."
            }
        ]
};

export { CHECKLIST_SCHEMA };
