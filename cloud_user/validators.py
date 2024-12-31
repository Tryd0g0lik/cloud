from django.core.exceptions import ValidationError
import re

def no_special_chars_validators(value:str):
  '''
  TODO: Validator to check if a value contains any special characters.
  :param value: type string.
  :return: True or Error
  '''

  for char in value:
    match = re.search(r'[A-Za-z_-]', char)
    if False if match != None else True:
      raise ValidationError('%(value)s contains invalid characters',
                            params={'value':value})
  return True

def min_length_validators(value: str):
  '''
  TODO: That is a checker string's length. Min length is three symbols
  :param value: type string.
  :return: True or Error
  '''
  if type(value) is not str:
    raise ValidationError('%(value) contains invalid type synbols',
                          params={'value': value})

  if len(value) < 3:
    raise ValidationError('%(value) contains invalid length. \
Min length is 3 symbols', params={'value': value})
  return True
