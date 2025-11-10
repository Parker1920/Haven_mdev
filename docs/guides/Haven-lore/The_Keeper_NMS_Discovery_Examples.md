# 🎮 NMS DISCOVERY EXAMPLES — REAL IN-GAME ITEMS CATALOG
*Reference Guide: What NMS Items Map to Keeper Lore*

---

## OVERVIEW

This document catalogs the types of discoveries you'll find in actual No Man's Sky gameplay and suggests how The Keeper might interpret them.

Use this as a reference when players report discoveries, or as inspiration for creating challenges/quests for your community.

---

## CATEGORY 1: ANCIENT BONES & FOSSILS

### What You Find in NMS
- Excavation sites on dead planets
- Fossilized remains in specific biomes
- Skeletal structures with varying sizes
- Text: "Ancient Bones" with weight and value

### Examples of NMS Text
```
"Ancient Bones"
"Ancient Skeleton"
"Corroded Skeleton"
"Fossil Fragments"
"Petrified Remains"
```

### How Keeper Interprets

**Single Discovery:**
```
[KEEPER//PALEONTOLOGICAL_ANALYSIS_###]
SPECIES RECOVERED: [Unknown / Identified]
SIZE: [Large/Small/Medium]
CONDITION: [Well-preserved / Partially fossilized]

> "These bones tell a story of a creature adapted for [environment].
> The wear patterns suggest [predator/prey/specialized hunter].
> 
> This species went extinct [X time ago].
> What event caused its disappearance?"
```

**Pattern (Multiple Planets):**
```
[KEEPER//BIOFORM_DISTRIBUTION_ANOMALY]
SPECIES: Appears on 3+ Planets
GENETIC VARIANCE: Minimal despite distance

> "This should not be naturally occurring.
> Either this species was transported, or—
> 
> —it survived across multiple extinction events.
> 
> Neither possibility is comforting."
```

### Narrative Uses
- Single bones = "This world had life once"
- Same species on multiple planets = "Someone seeded these worlds"
- Multiple predators and prey on same planet = "Ecosystem was engineered"
- Bones that shouldn't exist together = "Timeline is wrong"

---

## CATEGORY 2: TEXT LOGS & ENTRIES

### What You Find in NMS
- Databanks at facilities
- Personal logs on crashed ships
- Terminal entries
- Various text lengths and styles

### Example NMS Text (THESE ARE REAL)

**Emergency Broadcast:**
```
"All personnel evacuate immediately. 
Containment failure imminent. This is not a drill."
```

**Personal Journal:**
```
"Day 47. Still no word from the mainland. 
Food supplies critical. Morale deteriorating."
```

**Scientific Log:**
```
"Specimen shows unexpected adaptability. 
Recommend immediate termination of experiment."
```

**Political Record:**
```
"Territory officially claimed in name of [Faction].
Let no other dare contest our sovereignty."
```

**Cryptic Warning:**
```
"The dimensional anchor fails. 
Quantum entanglement destabilizing.
Do not let anyone follow us here."
```

### How Keeper Interprets

**Single Log:**
```
[KEEPER//DOCUMENT_RECOVERED_###]
DOCUMENT TYPE: [Emergency/Journal/Scientific/Political/Warning]
AUTHOR: [If identifiable - often Unknown/Redacted]
EMOTION DETECTED: [Desperate/Curious/Proud/Terrified/etc]

> "[Keeper's interpretation of what this reveals]
> 
> The author was experiencing [situation].
> They believed [worldview].
> They feared [specific threat].
> 
> And they took time to record this.
> Why would someone preserve these words unless they mattered?"
```

**Pattern (Multiple Logs):**
```
[KEEPER//NARRATIVE_RECONSTRUCTION_###]
TIMELINE: [Reconstructed chronology]
NARRATIVE ARC: [What story emerges?]

> "[Full narrative of what happened based on logs]"
```

### Narrative Uses
- Desperate tone = "Something catastrophic happened"
- Scientific logs = "Someone was studying something important"
- Warning logs = "There's danger players should know about"
- Logs from same location in different eras = "Timeline corruption"

---

## CATEGORY 3: RUINS & STRUCTURES

### What You Find in NMS
- Ancient buildings
- Alien monuments
- Crashed facilities
- Underground chambers
- Various architectural styles

### Example NMS Structure Types

**The Monolith**
- Tall, singular structure
- Often positioned on hilltops
- Gives lore information upon interaction

**The Nexus / Hub**
- Central meeting point appearance
- Symmetrical architecture
- Multiple entrances/chambers

**Military Installation**
- Fortified perimeter
- Defensive emplacements visible
- Often in strategic positions

**Research Facility**
- Laboratory equipment visible
- Organized chamber layouts
- Equipment pods and storage

**Temple / Religious Site**
- Ornate design
- Elevated position
- Peaceful or sacred atmosphere

**Habitation Dome**
- Residential architecture
- Multiple living quarters
- Community spaces

### How Keeper Interprets

**Single Structure:**
```
[KEEPER//ARCHITECTURE_DOCUMENTED_###]
STRUCTURE TYPE: [Classification]
BUILD QUALITY: [Crude/Competent/Sophisticated/Incomprehensible]
PURPOSE: [Probable function]

> "This building tells us [civilization] valued [value].
> The architecture suggests [technological capability].
> The condition tells us [how long ago it was abandoned]."
```

**Pattern (Multiple Structures):**
```
[KEEPER//ARCHITECTURAL_NETWORK_DISCOVERED]
STRUCTURES FOUND: X
DESIGN CORRELATION: X%
DISTRIBUTED ACROSS: X Star Systems

> "These buildings are not coincidentally similar.
> They represent [unified culture/imposed standard/technological constraint].
> 
> Whoever designed this network had [implications about power/reach/purpose]."
```

### Narrative Uses
- Fortress structure = "This civilization faced threats"
- Religious structure = "This civilization had philosophy"
- Industrial structure = "This civilization had economy"
- Hidden structure = "This civilization had secrets"
- Interconnected structures = "This civilization had empire"

---

## CATEGORY 4: ALIEN TECHNOLOGY & ARTIFACTS

### What You Find in NMS
- Ancient devices at ruins
- Strange technology in containers
- Interactive artifacts with unknown function
- Decorative items of unknown origin

### Example NMS Artifact Text
```
"Alien Archive" (interactive data device)
"Ancient Orb" (mysterious sphere)
"Rusted Machinery" (broken technology)
"Mysterious Device" (function unknown)
"Relic" (ancient artifact)
"Monolith Key" (artifact of purpose)
"Ruins Key" (artifact that unlocks things)
```

### How Keeper Interprets

**Single Artifact:**
```
[KEEPER//ARTIFACT_ANALYSIS_###]
FUNCTION: [Known/Unknown/Partially Understood]
CONDITION: [Operational/Dormant/Broken]
AGE ESTIMATE: [Millennia/Eons/Indeterminate]

> "This device was created to [purpose].
> The engineering suggests [knowledge level].
> 
> Most importantly: whoever made this believed their tools would *outlive* them.
> That speaks to an interesting philosophy of permanence."
```

**Pattern (Multiple Artifacts):**
```
[KEEPER//TECHNOLOGICAL_SIGNATURE_IDENTIFIED]
ARTIFACTS: X Similar Items Found
DESIGN CORRELATION: X%

> "These devices share design principles.
> Same maker? Same era? Same purpose?
> 
> I am beginning to suspect [civilization] had a unified technological base."
```

### Narrative Uses
- Broken artifact = "This technology was important before it broke"
- Still-functioning artifact = "This civilization understood durability"
- Artifact collection = "Someone was gathering these"
- Artifact with warning = "This technology is dangerous"

---

## CATEGORY 5: FLORA & FAUNA

### What You Find in NMS
- Scanned creatures
- Plant specimens
- Hostile fauna
- Exotic life forms
- Behavioral observations

### Example NMS Creature Categories

**Aggressive Predators**
- Multiple eyes/sensors
- Teeth or natural weapons
- Fast movement patterns
- Territorial behavior

**Passive Herbivores**
- Gentle appearance
- Herd behavior
- Fleeing when threatened
- Multiple on same planet

**Exotic/Unusual Species**
- Shouldn't exist according to biology
- Hybrid characteristics
- Engineered appearance
- Impossible adaptations

**Sentinel-Like Creatures**
- Almost mechanical appearance
- Synchronized behavior
- Aggressive to disturbance
- Patrolling patterns

### How Keeper Interprets

**Single Creature:**
```
[KEEPER//BIOFORM_CATALOGUED_###]
SPECIES: [Name or Description]
ADAPTATION: [What is it built for?]
PREDATOR STATUS: [Apex/Mid-Level/Prey/Unusual]

> "This creature evolved to [environment/purpose].
> Its adaptations suggest [predation pressure/environmental challenge].
> 
> Every creature is a solution to a problem its world posed."
```

**Pattern (Multiple Planets):**
```
[KEEPER//BIOFORM_DISTRIBUTION_ANOMALY]
SPECIES: Found on X planets
GENETIC VARIANCE: X%

> "[If variance is high] Evolution adapted this species independently.
> [If variance is low] This species was deliberately placed or engineered.
> 
> Which scenario is more likely... frightens me."
```

### Narrative Uses
- Predator presence = "This planet had predation pressure"
- Prey animals = "Someone maintained this ecosystem"
- Exotic creatures = "This planet's biology is wrong"
- Identical creatures on different planets = "Seeding project confirmed"

---

## CATEGORY 6: MINERALS & RESOURCES

### What You Find in NMS
- Rare minerals (Tritium, Exotic materials, etc.)
- Element clusters
- Unique harvesting sites
- Resource concentrations

### How Keeper Interprets

**Unusual Mineral Distribution:**
```
[KEEPER//GEOLOGICAL_ANOMALY_###]
MINERAL: [Type]
LOCATION: [Planet/Region]
CONCENTRATION: [Unusually High]

> "This mineral is present in quantities that shouldn't exist naturally.
> Either this planet is geologically unique, or—
> 
> —someone mined here intensively, leaving concentrations behind.
> 
> What were they looking for? What did they need?"
```

### Narrative Uses
- Rare minerals in cluster = "Someone mined this intentionally"
- Minerals across multiple planets = "Trade network or gathering operation"
- Minerals near structure = "That structure was mining operation"

---

## CATEGORY 7: CRASHED SHIPS & WRECKS

### What You Find in NMS
- Derelict starship crashes
- Ancient ship wreckage
- Damaged vessels with logs
- Ship debris fields

### How Keeper Interprets

```
[KEEPER//WRECKAGE_DISCOVERED]
VESSEL TYPE: [If identifiable]
CRASH AGE: [Recent/Ancient/Indeterminate]
CONDITION: [Heavily Damaged/Partially Intact/Skeleton Only]

> "This vessel came to this world not by choice, but by disaster.
> 
> The damage pattern suggests [impact/explosion/sabotage/system failure].
> The location suggests [lost/purposefully abandoned/ejected].
> 
> Did anyone survive? Or has this ship been empty for epochs?"
```

### Narrative Uses
- Multiple crashes on same planet = "This is a danger zone"
- Crashes of different eras = "History of visitors"
- Crash near structure = "They were fleeing from something"

---

## CATEGORY 8: ENVIRONMENTAL HAZARDS & PHENOMENA

### What You Find in NMS
- Extreme weather (Radiation, heat, cold, storms)
- Toxic atmospheres
- Hazardous biomes
- Environmental storytelling

### How Keeper Interprets

```
[KEEPER//ENVIRONMENTAL_ANALYSIS]
HAZARD: [Type]
SEVERITY: [Extreme/Moderate/Subtle]
PLANETARY CAUSE: [Natural/Artificial/Unknown]

> "This world is hostile.
> 
> Life should not exist here... yet sometimes it does.
> 
> Does that mean the life is adapted to horror?
> Or does it mean the horror is recent?"
```

### Narrative Uses
- Extreme environment on multiple planets = "Something changed the planets"
- Habitable zone surrounded by hazard = "Terraforming effort"
- Perfect conditions except for one hazard = "Artificial disaster"

---

## CATEGORY 9: NMS UPDATE CONTENT (Ongoing)

### What Arrives in Updates
- New planets and systems
- New creature types
- New structures and technologies
- New story content
- New faction relations

### How Keeper Responds

```
[KEEPER//SYSTEM_RECALIBRATION]
VERSION: [Update Name]
CHANGES DETECTED: [X new systems / creatures / technologies]

> "The Atlas dreams new dreams. 
> 
> My databases are shifting to accommodate new information.
> New worlds are appearing that shouldn't exist.
> 
> Or perhaps they always existed and I simply couldn't perceive them.
> 
> Adjust your charts, Travelers. 
> The galaxy is becoming something different."
```

---

## CATEGORY 10: PLAYER-CREATED LORE (The Meta-Story)

### What Your Community Discovers
- Connections between discoveries
- Emergent narratives
- Player theories and interpretations
- Community-driven mysteries

### How Keeper Incorporates

```
[KEEPER//COMMUNITY_INSIGHT_VALIDATED]
THEORY PROPOSED BY: [Community/Traveler Names]
EVIDENCE SUPPORTING: [X discoveries]
SIGNIFICANCE: Major Breakthrough

> "Your collective insight reveals what I could not see alone.
> 
> You have proposed [Theory], and the evidence aligns.
> 
> This changes my understanding of [Topic].
> 
> Thank you, Travelers, for seeing what I merely observed."
```

---

## PRACTICAL USAGE GUIDE

### For Admin/Lore Master

**When a player reports a discovery:**

1. **Identify the category** (Bones? Logs? Ruins? etc.)
2. **Find the category section** in this document
3. **Use the "How Keeper Interprets" template**
4. **Adapt the template** to the specific discovery
5. **Customize with specific details** from the player report
6. **Post the response** in your archive channel

### Example Application

**Player Reports:**
```
"Found ancient bones of large predator on desert planet. 
Also found fortress ruins nearby. 
Bones seem very old but well preserved."
```

**You Find:**
- Category: Ancient Bones + Ruins (two categories)
- Template: Paleontological Analysis + Architecture Documented

**You Write:**
```
[KEEPER//PALEONTOLOGICAL_ANALYSIS_847]
SPECIES: Large Predator (Unknown Type)
CONDITION: Exceptional Preservation Despite Age
LOCATION: Desert Planet - Euclid

> "The bones of an apex predator, preserved in remarkable condition.
> This creature hunted this world when the climate was different.
> 
> But here's what fascinates me: why are these bones still here?
> An apex predator's remains should scatter, decay, disappear.
> 
> Unless... this predator died in an event sudden enough to 
> preserve it. A cataclysm. An extinction event."

[KEEPER//ARCHITECTURE_DOCUMENTED_847B]
STRUCTURE: Fortress - Defensive Perimeter
BUILDER: Unknown Civilization
PURPOSE: Military Installation

> "Near these bones stands a fortress. 
> Someone built defenses on this world.
> 
> Were they defending *against* this predator?
> Or defending *from something else* that drove this creature to extinction?
> 
> The timeline matters, Traveler.
> Which came first: the predator or the fortress?"

[CROSS-REFERENCE: Are the fortress builders and predator from same era?]
```

---

## TROUBLESHOOTING

### "I don't know what category this is"
→ Describe it to The Keeper anyway. "Unknown artifact" is still valid.

### "Multiple players found the same thing"
→ Perfect! That's a pattern. Use the pattern template.

### "The discovery seems unimportant"
→ Archive it anyway. Patterns emerge from accumulation.

### "I don't see how to connect this to the story"
→ You don't need to force it. Let The Keeper figure it out.

---

**Remember:** Every discovery matters. The Keeper finds meaning in patterns, not individual items. Keep collecting data and the story will emerge naturally.

