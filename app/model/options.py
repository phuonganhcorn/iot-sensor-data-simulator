from model.models import OptionsModel


class Options(OptionsModel):

    @staticmethod
    def get_option(name):
        return Options.session.query(OptionsModel).filter_by(name=name).first()

    @staticmethod
    def set_option(name, value):
        option = OptionsModel.get_option(name)
        if option is None:
            option = OptionsModel(name=name, value=value)
            OptionsModel.session.add(option)
        else:
            option.value = value
        OptionsModel.session.commit()
        return option
