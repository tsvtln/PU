prfx = ["CSM4", "LAB4"]
name = "LAB4VDACRSG001"

if any(p in name for p in prfx):
    print("Found prefix in name")