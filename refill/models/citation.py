import dateparser
from datetime import date


class Citation:
    FIELDS = {
        'type': str,
        'url': str,
        'title': str,
        'date': date,
        'accessdate': date,
        'authors': list,
        'editors': list,
        'publisher': str,
        'work': str,
        'website': str,
        'archiveurl': str,
        'archivedate': date,
        'deadurl': bool,
        'via': str,
        'journal': str,
        'volume': str,
        'issue': str,
        'pages': str,
        'pmid': str,
        'pmc': str,
        'doi': str,
    }

    def __init__(self, **kwargs):
        for field, ftype in Citation.FIELDS.items():
            if ftype is date:
                self.__dict__[field] = None
            else:
                self.__dict__[field] = ftype()

        self.type = 'webpage'

        for field, value in kwargs.items():
            self[field] = value

    def __setattr__(self, field: str, value: str):
        self.__dict__[field] = self.__cleanValue(field, value)

    def __getattr__(self, field: str):
        self.__assertValidField(field)
        return self.__dict__[field]

    def __setitem__(self, field: str, value: str):
        self.__setattr__(field, value)

    def __getitem__(self, field: str):
        return self.__getattr__(field)

    def __contains__(self, field: str):
        return bool(getattr(self, field))

    def __iter__(self):
        for field in Citation.FIELDS:
            if field in self:
                yield (field, getattr(self, field))

    def __eq__(self, operand):
        if not isinstance(operand, self.__class__):
            return False

        return self.__dict__ == operand.__dict__

    def addAuthor(self, author: str):
        self.authors.append(author)

    def removeAuthor(self, author: str):
        self.authors.remove(author)

    def merge(self, citation: 'Citation'):
        for key, value in citation.__dict__.items():
            if value:
                self.__dict__[key] = value

    # Private

    def __assertValidField(self, field):
        if field not in Citation.FIELDS:
            raise NameError('Invalid field: {}'.format(field))

        return True

    def __cleanValue(self, field, value):
        self.__assertValidField(field)

        ftype = Citation.FIELDS[field]

        if ftype is date and type(value) is str:
            d = dateparser.parse(value)
            if not d:
                raise ValueError('Invalid date {}'.format(value))
            return d.date()
        elif not type(value) is ftype:
            raise ValueError('Invalid value {} for field {}'.format(value, field))

        if type(value) is str:
            value = value.strip()

        return value
