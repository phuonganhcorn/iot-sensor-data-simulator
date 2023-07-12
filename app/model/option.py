from model.models import OptionModel


class Option(OptionModel):

    @staticmethod
    def _get_option(name):
        return Option.session.query(OptionModel).filter_by(name=name).first()
    
    @staticmethod
    def get_value(name):
        option = Option._get_option(name)
        if option is not None:
            return option.value
        return None
    
    @staticmethod
    def get_boolean(name):
        value = Option.get_value(name)
        if value is None:
            return False
        return value == "1"

    @staticmethod
    def set_option(name, value):
        option = Option._get_option(name)
        if option is None:
            option = Option(name=name, value=value)
            Option.session.add(option)
        else:
            option.value = value
        Option.session.commit()
        return option
    

