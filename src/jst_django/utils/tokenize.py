class Tokenize:

    def __init__(self, code: str):
        self.code = code
        self.properties = {}

    def _get_field(self, field_type, field):
        match field_type:
            case "char":
                return f'models.CharField(verbose_name=_("{field}"), max_length=255)'
            case "text":
                return f'models.TextField(verbose_name=_("{field}"))'
            case "int":
                return f'models.IntegerField(verbose_name=_("{field}"))'
            case "image":
                return f'models.ImageField(verbose_name=_("{field}"), upload_to="{field}s")'
            case "bool":
                return f'models.BooleanField(verbose_name=_("{field}"))'
            case "date":
                return f'models.DateField(verbose_name=_("{field}"))'
            case "time":
                return f'models.TimeField(verbose_name=_("{field}"))'
            case "datetime":
                return f'models.DateTimeField(verbose_name=_("{field}"))'
            case _:
                return f'models.CharField(verbose_name=_("{field}"), max_length=255)'

    def _parse_field(self, field: str) -> list:
        field_parts = field.split(":")
        size_field_parts = len(field_parts)
        if size_field_parts != 2:
            raise Exception("fields not validated")
        return field_parts[0], self._get_field(field_parts[-1], field_parts[0])

    def make(self):
        fields = self.code.split(",")
        for field in fields:
            name, value = self._parse_field(field)
            self.properties[name] = value
        return self

    @property
    def keys(self):
        return self.properties.keys()

    @property
    def items(self):
        return self.properties

    @property
    def model(self):
        res = []
        for field, property in self.properties.items():
            res.append(f"{field} = {property}")
        return res
