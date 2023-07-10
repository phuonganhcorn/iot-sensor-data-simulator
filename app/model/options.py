from model.models import OptionsModel


class Options(OptionsModel):

    @staticmethod
    def _get_option(name):
        return Options.session.query(OptionsModel).filter_by(name=name).first()
    
    @staticmethod
    def get_value(name):
        return Options._get_option(name).value
    
    @staticmethod
    def get_boolean(name):
        value = Options.get_value(name)
        if value is None:
            return False
        return value == "1"

    @staticmethod
    def set_option(name, value):
        option = Options._get_option(name)
        if option is None:
            option = Options(name=name, value=value)
            Options.session.add(option)
        else:
            option.value = value
        Options.session.commit()
        return option
    

