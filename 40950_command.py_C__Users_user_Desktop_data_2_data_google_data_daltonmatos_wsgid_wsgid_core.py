from plugnplay import Interface


class ICommand(Interface):

    def command_name(self):
        """
        Returns the command name. This name will be used to show aditional
        options when calling wsgid --help
        """
        pass

    def name_matches(self, command_name):
        """
        Returns True if this command implementor
        can run the command passed as {command_name} parameter
        Returns False otherwise
        """
        pass

    def run(self, options, command_name=None):
        """
        Officially runs the command and receive the same options that
        was passed on the command line

        The optional command_name parameter is useful when you have the same
        implementation for two different commands

        Retuns nothing
        """
        pass

    def extra_options(self):
        """
        Return a list of wsgid.options.parser.CommandLineOption instances
        """
        pass
