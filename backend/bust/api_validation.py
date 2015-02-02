class ValidationError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super(Exception, self).__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def message_to_dict(self):
        return {
            'status' : self.status_code,
            'message' : self.message,
        }

class ArgumentValidation(object):
    @classmethod
    def validate_and_get_float_arg_values(cls, request_args, required_args, optional_args=[]):
        cls.validate_float_args(request_args, required_args, optional_args)
        arg_values = cls.get_arg_values(request_args, required_args, optional_args)
        if type(arg_values) is list:
            for ii in range(len(arg_values)):
                if arg_values[ii] is not None:
                    arg_values[ii] = float(arg_values[ii])
        else:
            if arg_values is not None:
                arg_values = float(arg_values)
        return arg_values

    @classmethod
    def validate_and_get_arg_values(cls, request_args, required_args, optional_args=[]):
        cls.validate_args(request_args, required_args)
        return cls.get_arg_values(request_args, required_args, optional_args)

    @classmethod
    def validate_float_args(cls, request_args, required_args, optional_args=[]):
        cls.validate_args(request_args, required_args)
        try:
            for arg in required_args + optional_args:
                if arg in request_args:
                    float(request_args[arg])
        except (TypeError, ValueError) as e:
            message = 'Bad Request: {0} is not a valid parameter value'\
                .format(request_args[arg])
            raise ValidationError(message)

    @classmethod
    def validate_args(cls, request_args, required_args):
        try:
            for arg in required_args:
                request_args[arg]
        except KeyError as e:
            message = 'Bad Request: Request does not contain the {0} parameter'.format(e.message)
            raise ValidationError(message)
    
    @classmethod
    def get_arg_values(cls, request_args, required_args, optional_args=[]):
        arg_values = []
        for arg in required_args + optional_args:
            if arg in request_args:
                arg_values.append(request_args[arg])
            else:
                arg_values.append(None)
        if len(arg_values) == 1:
            arg_values = arg_values[0]
        return arg_values
