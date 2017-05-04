class Utils:
    def homogenizeTemplateName(name: str):
        name = name.strip()
        if not name:
            return name
        return name[0].upper() + name[1:]
