"""Library of decorators to validate certain tests
or to catch expected exceptions"""

import functools
from jpegdna.coders import NonDecodableCategory, NonDecodableGoldman
from jpegdna.coders import (AutomataSetterException as SetterCoderError,
                            AutomataGetterException as GetterCoderError,
                            AutomataSetterExceptionEncode as SetterEncodeCoderError,
                            AutomataSetterExceptionDecode as SetterDecodeCoderError,
                            AutomataGetterExceptionEncode as GetterEncodeCoderError,
                            AutomataGetterExceptionDecode as GetterDecodeCoderError)
from jpegdna.transforms import (AutomataSetterExceptionForward as SetterForwardTransformError,
                                AutomataSetterExceptionInverse as SetterInverseTransformError,
                                AutomataGetterExceptionForward as GetterForwardTransformError,
                                AutomataGetterExceptionInverse as GetterInverseTransformError)
from jpegdna.format import (AutomataSetterExceptionFormat as SetterFormatError,
                            AutomataSetterExceptionDeformat as SetterDeformatError,
                            AutomataGetterExceptionFormat as GetterFormatError,
                            AutomataGetterExceptionDeformat as GetterDeformatError)

def generate_decorator(exception):
    """Ddecorator generator"""
    def expected_error(test):
        @functools.wraps(test)
        def inner(*args, **kwargs):
            try:
                test(*args, **kwargs)
            except exception:
                assert True
            else:
                raise AssertionError(exception().__class__.__name__ + ' expected')
        return inner
    return expected_error

expected_value_error = generate_decorator(ValueError)
expected_type_error = generate_decorator(TypeError)
expected_index_error = generate_decorator(IndexError)
expected_non_decodable_category = generate_decorator(NonDecodableCategory)
expected_non_decodable_goldman = generate_decorator(NonDecodableGoldman)
expected_setter_encode_coder_error = generate_decorator(SetterEncodeCoderError)
expected_setter_decode_coder_error = generate_decorator(SetterDecodeCoderError)
expected_setter_coder_error = generate_decorator(SetterCoderError)
expected_getter_encode_coder_error = generate_decorator(GetterEncodeCoderError)
expected_getter_decode_coder_error = generate_decorator(GetterDecodeCoderError)
expected_getter_coder_error = generate_decorator(GetterCoderError)
expected_setter_forward_transform_error = generate_decorator(SetterForwardTransformError)
expected_setter_inverse_transform_error = generate_decorator(SetterInverseTransformError)
expected_getter_forward_transform_error = generate_decorator(GetterForwardTransformError)
expected_getter_inverse_transform_error = generate_decorator(GetterInverseTransformError)
expected_setter_format_error = generate_decorator(SetterFormatError)
expected_setter_deformat_error = generate_decorator(SetterDeformatError)
expected_getter_format_error = generate_decorator(GetterFormatError)
expected_getter_deformat_error = generate_decorator(GetterDeformatError)
