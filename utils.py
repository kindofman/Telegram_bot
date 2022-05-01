def process_name(name, status):
    if status == 0:
        suffix = ""
    elif status == 1:
        suffix = " ✅"
    elif status == 2:
        suffix = " 🆕"
    return name + suffix
