"""
Sample Data and Demonstration Scenarios for Multimodal Construction Intelligence Platform.
Contains pre-configured inspection scenarios, realistic OSHA/IS 456 audit reports,
crack diagnostic datasets, and synthetic image generators for 1-click testing.
"""

import io
from PIL import Image, ImageDraw, ImageFont


def create_synthetic_site_image(scenario: str = "scaffolding") -> Image.Image:
    """
    Generates a realistic synthetic construction site graphic using PIL.
    Ensures zero external dependency or broken links when testing without file uploads.
    """
    width, height = 800, 500
    img = Image.new("RGB", (width, height), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)

    # Background sky and ground
    draw.rectangle([0, 0, width, int(height * 0.6)], fill=(51, 65, 85)) # Sky/dusk
    draw.rectangle([0, int(height * 0.6), width, height], fill=(71, 85, 105)) # Ground/concrete slab

    if scenario == "scaffolding":
        # Scaffolding pipes (yellow/galvanized)
        for x in range(100, 750, 120):
            draw.line([(x, 50), (x, 420)], fill=(203, 213, 225), width=6)
        for y in range(80, 450, 70):
            draw.line([(80, y), (720, y)], fill=(203, 213, 225), width=5)
            # Diagonal braces
            draw.line([(80, y), (200, y + 70)], fill=(148, 163, 184), width=3)
            draw.line([(200, y + 70), (320, y)], fill=(148, 163, 184), width=3)
        
        # Working platform planks
        draw.rectangle([100, 200, 700, 215], fill=(180, 83, 9))
        draw.rectangle([100, 340, 700, 355], fill=(180, 83, 9))

        # Worker 1 (Platform - High-Vis Vest + Yellow Helmet)
        # Helmet
        draw.ellipse([240, 140, 270, 165], fill=(234, 179, 8)) # Helmet
        # Head
        draw.ellipse([245, 155, 265, 175], fill=(226, 170, 140))
        # Torso with High-Vis Orange vest + reflective stripes
        draw.rectangle([235, 175, 275, 205], fill=(249, 115, 22))
        draw.line([(242, 175), (242, 205)], fill=(248, 250, 252), width=3)
        draw.line([(268, 175), (268, 205)], fill=(248, 250, 252), width=3)
        # Harness tether (connected to lifeline)
        draw.line([(255, 180), (255, 80)], fill=(16, 185, 129), width=3) # Fall arrest lanyard

        # Worker 2 (Lower deck - Missing Harness & Defective Vest)
        draw.ellipse([500, 280, 530, 305], fill=(255, 255, 255)) # White helmet
        draw.ellipse([505, 295, 525, 315], fill=(210, 150, 120))
        draw.rectangle([495, 315, 535, 345], fill=(59, 130, 246)) # Plain blue shirt (NO HIGH-VIS)

        # Danger indicator
        draw.ellipse([485, 270, 545, 355], outline=(239, 68, 68), width=3)

    elif scenario == "excavation":
        # Deep trench excavation cut
        draw.polygon([(0, 200), (250, 480), (550, 480), (800, 200), (800, 500), (0, 500)], fill=(69, 44, 26))
        # Rebar cage inside trench
        for rx in range(300, 500, 25):
            draw.line([(rx, 350), (rx, 470)], fill=(156, 163, 175), width=4)
        for ry in range(370, 470, 25):
            draw.line([(280, ry), (520, ry)], fill=(156, 163, 175), width=4)

        # Excavator boom outline
        draw.line([(680, 120), (520, 260)], fill=(234, 179, 8), width=18)
        draw.line([(520, 260), (460, 360)], fill=(234, 179, 8), width=14)
        # Bucket
        draw.polygon([(440, 360), (470, 390), (430, 410)], fill=(30, 41, 59))

        # Worker near excavator bucket (Severe Zone hazard)
        draw.ellipse([380, 380, 405, 400], fill=(234, 179, 8)) # Helmet
        draw.rectangle([375, 400, 410, 440], fill=(34, 197, 94)) # High Vis green vest

    else: # Hot works / General
        # Steel I-Beam structure
        draw.rectangle([150, 100, 200, 450], fill=(71, 85, 105))
        draw.rectangle([580, 100, 630, 450], fill=(71, 85, 105))
        draw.rectangle([100, 180, 700, 230], fill=(100, 116, 139))
        # Welding arc flare
        draw.ellipse([360, 190, 420, 250], fill=(254, 240, 138))
        draw.ellipse([380, 210, 400, 230], fill=(255, 255, 255))
        # Welder with welding shield
        draw.rectangle([340, 190, 370, 230], fill=(30, 41, 59)) # Welding mask

    # Watermark overlay
    draw.rectangle([20, 20, 360, 56], fill=(15, 23, 42, 200))
    draw.text((30, 25), "SIMULATED TELEMETRY FEED", fill=(245, 158, 11))
    draw.text((30, 40), f"Site Area: Sector 4C | Standard: OSHA 1926 & IS 456", fill=(148, 163, 184))

    return img


def create_synthetic_crack_image(defect_type: str = "structural_shear") -> Image.Image:
    """
    Generates a realistic synthetic concrete crack surface image.
    """
    width, height = 700, 450
    # Concrete texture background (light grey concrete surface)
    img = Image.new("RGB", (width, height), color=(185, 190, 195))
    draw = ImageDraw.Draw(img)

    # Concrete speckles / aggregate roughness
    import random
    rng = random.Random(42)
    for _ in range(1200):
        sx = rng.randint(0, width - 1)
        sy = rng.randint(0, height - 1)
        c = rng.randint(140, 215)
        draw.point((sx, sy), fill=(c, c, c))

    # Formwork joint lines
    draw.line([(0, 60), (width, 60)], fill=(150, 155, 160), width=2)
    draw.line([(0, 380), (width, 380)], fill=(150, 155, 160), width=2)

    if defect_type == "structural_shear":
        # Critical 45-degree diagonal shear crack across concrete beam-column joint
        points = [
            (140, 400), (220, 330), (290, 270), (360, 230),
            (420, 180), (480, 140), (550, 90), (600, 50)
        ]
        # Jitter the crack path
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            draw.line([p1, p2], fill=(20, 20, 25), width=6)
            # Secondary branch
            if i in [2, 4]:
                draw.line([p1, (p1[0] + 35, p1[1] - 40)], fill=(40, 40, 45), width=3)

    elif defect_type == "spalling":
        # Concrete spalling with rusted exposed rebar
        draw.ellipse([260, 150, 460, 310], fill=(130, 120, 115))
        # Exposed corroded rebar
        draw.rectangle([230, 210, 490, 235], fill=(153, 60, 20)) # Rust rebar
        draw.line([(230, 222), (490, 222)], fill=(194, 65, 12), width=3)
        # Delamination borders
        draw.arc([250, 140, 470, 320], 0, 360, fill=(40, 40, 40), width=4)

    else: # Hairline crack
        # Fine meandering drying shrinkage hairline crack
        points = [
            (200, 40), (230, 110), (220, 180), (250, 250),
            (240, 320), (260, 410)
        ]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=(60, 60, 65), width=2)

    # Metric scale ruler watermark
    draw.rectangle([width - 150, height - 50, width - 20, height - 20], fill=(255, 255, 255))
    draw.line([(width - 140, height - 35), (width - 30, height - 35)], fill=(0, 0, 0), width=3)
    for x in range(width - 140, width - 25, 22):
        draw.line([(x, height - 42), (x, height - 28)], fill=(0, 0, 0), width=2)
    draw.text((width - 110, height - 48), "10 mm", fill=(0, 0, 0))

    return img


# Demonstration Mock Data for Tab 1 (Site Safety & PPE Audit)
DEMO_SAFETY_AUDIT = {
    "safety_score": 68,
    "overall_status": "Action Required",
    "status_level": "medium",
    "worker_count": 5,
    "compliant_workers": 3,
    "compliance_percentage": 60.0,
    "standards_evaluated": [
        "OSHA 29 CFR 1926.100 (Head Protection)",
        "OSHA 29 CFR 1926.501 (Fall Protection)",
        "IS 456:2000 (Safety & Construction Practice)",
        "IS 2925:1984 (Industrial Hard Hats)",
        "IS 15298 (Safety Footwear)",
        "IS 3521 (Industrial Safety Belts and Harnesses)"
    ],
    "ppe_detection": [
        {"item": "Industrial Safety Helmet (Hard Hat)", "detected_count": 4, "total_workers": 5, "compliance_pct": 80, "status": "Partial Non-Compliance"},
        {"item": "High-Visibility Safety Vest (Class 2/3)", "detected_count": 3, "total_workers": 5, "compliance_pct": 60, "status": "Action Required"},
        {"item": "Steel-Toe Protective Footwear", "detected_count": 4, "total_workers": 5, "compliance_pct": 80, "status": "Satisfactory"},
        {"item": "Safety Harness / Fall Arrest System", "detected_count": 2, "workers_at_height": 3, "compliance_pct": 66, "status": "Critical Gap"}
    ],
    "identified_site_hazards": [
        {
            "id": "HAZ-001",
            "hazard_title": "Worker at Height (>3m) Unanchored Lifeline",
            "location": "Upper Scaffolding Staging - Sector 4C",
            "severity": "Critical",
            "osha_clause": "OSHA 1926.501(b)(1) & IS 3521",
            "observation": "Worker observed standing on planking at elevation above 10 feet without lanyard securely hitched to static lifeline or anchorage point.",
            "corrective_remedy": "Immediate work stoppage for worker. Enforce 100% tie-off protocol with shock-absorbing dual lanyards anchored to certified 5,000-lb rated attachment points."
        },
        {
            "id": "HAZ-002",
            "hazard_title": "Missing High-Visibility Retro-Reflective Vest",
            "location": "Ground staging & forklift maneuvering perimeter",
            "severity": "High",
            "osha_clause": "OSHA 1926.201 & NBC 2016 Part 7",
            "observation": "One personnel operating adjacent to heavy equipment swing corridor wearing dark civilian attire with zero retro-reflective markings.",
            "corrective_remedy": "Provide EN ISO 20471 / IS fluorescent class 3 safety vest prior to allowing access to mobile machinery transit zones."
        },
        {
            "id": "HAZ-003",
            "hazard_title": "Incomplete Scaffolding Toe-Boards & Mid-Rails",
            "location": "Perimeter working deck level 2",
            "severity": "Medium",
            "osha_clause": "OSHA 1926.451(g)(4) & IS 4014",
            "observation": "Scaffold edge lacking 4-inch toe-board; tools and masonry debris present risk of drop hazard to workers beneath.",
            "corrective_remedy": "Install standardized 100mm timber/steel toe-boards and safety mesh debris nets along open scaffold perimeters."
        }
    ]
}

# Demonstration Mock Data for Tab 2 (Crack Diagnostics & Structural Integrity)
DEMO_CRACK_DIAGNOSTICS = {
    "defect_classification": "Structural Shear Crack",
    "structural_element": "Reinforced Concrete Beam-Column Joint (Exterior Framing)",
    "estimated_crack_width_mm": 2.8,
    "width_tolerance_rating": "Exceeds IS 456 Permissible Limit (0.3mm Max)",
    "estimated_length_cm": 64.0,
    "depth_profile": "Deep Through-Section Penetration (>45mm)",
    "urgency": "Immediate Repair (Critical)",
    "root_causes": [
        "Excessive diagonal tension shear stresses exceeding concrete shear capacity (τ_c)",
        "Inadequate or widely spaced shear stirrups / link ties per IS 13920 seismic ductile detailing",
        "Differential settlement of foundation corner footing transferring unanticipated rotational moment",
        "Recent structural live load redistribution during floor slab casting"
    ],
    "engineering_standards": [
        "IS 456:2000 Table 19 & Clause 40 (Shear Reinforcement)",
        "IS 13920:2016 (Ductile Detailing of RC Structures Subjected to Seismic Forces)",
        "ACI 224.1R (Causes, Evaluation, and Repair of Cracks in Concrete Structures)",
        "ACI 503R (Use of Epoxy Compounds with Concrete)"
    ],
    "recommended_repairs": [
        {
            "step": 1,
            "procedure": "Surface Preparation & Port Installation",
            "specification": "V-groove chase 15mm deep along crack line; blow out dust with oil-free compressed air; bond injection ports at 200mm intervals using rapid-setting polyester epoxy paste."
        },
        {
            "step": 2,
            "procedure": "Low-Viscosity Epoxy Pressure Injection",
            "specification": "Inject high-modulus, ultra-low viscosity structural epoxy resin (ASTM C881 Type I/IV Grade 1) under 2-4 bar sustained pressure from lowest port upward until refusal."
        },
        {
            "step": 3,
            "procedure": "Carbon Fiber Reinforced Polymer (CFRP) Strengthening",
            "specification": "Apply bi-directional CFRP wrapping (300 g/m² high-tensile carbon fabric impregnated with epoxy saturant) in U-jacket configuration to restore and augment shear resistance."
        },
        {
            "step": 4,
            "procedure": "Non-Destructive Ultrasonic Pulse Velocity (UPV) Verification",
            "specification": "Perform UPV grid testing 7 days post-grouting to verify complete void filling and acoustic velocity > 3800 m/s per IS 516 (Part 5)."
        }
    ]
}
