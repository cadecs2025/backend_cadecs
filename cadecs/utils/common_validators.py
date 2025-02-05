import re
from ipaddress import ip_address

from django.core.validators import validate_email


VALIDATION = {
    "common": {"min": 3, "max": 50},
    "common2": {"min": 1, "max": 100},
    "firstName": {"min": 3, "max": 20},
    "lastName": {"min": 3, "max": 20},
    "mobileNumber": {"min": 9, "max": 15},
    "emailSubject": {"min": 3},
    "passwordNormal": {"min": 8, "max": 50},
    "securityName": {"min": 3, "max": 150},
    "deleteReason": {"min": 3, "max": 199},
}


class FieldValidator:
    
    @staticmethod
    def specialchar_validator(text, include_char=[]):
        char_combination = ['[','^']
        char_combination.extend(include_char)
        char_combination.append(']')
        valid_char = ''.join(char_combination)
        pattern = re.compile(valid_char)
        match = pattern.search(text)
        if match:
            return False
        else:
            return True

    @staticmethod
    def ipAddress_validator(ip):
        try:
            ip_address(ip)
        except Exception:
            return False
        else:
            return True

    @staticmethod
    def port_validator(field):
        try:
            field = int(field)
        except Exception:
            return False
        if field > 0 and field < 65536:
            return True
        else:
            return False

    @staticmethod
    def email_validator(email):
        try:
            validate_email(email)
        except Exception:
            return False
        else:
            return True

    @staticmethod
    def email_subject_validator(field):
        # reg = "^[A-Za-z0-9_. \-,]{3,200}$"
        reg = r"^[A-Za-z0-9_. \-,\\/]{3,200}$"
        if re.match(reg, field):
            return True
        return False

    @staticmethod
    def common_name_validator(field):
        reg = "^[A-Za-z]{3,50}$"
        if re.match(reg, field):
            return True
        return False


    @staticmethod
    def rule_name_validator(field):
        # reg = "^[A-Za-z0-9_\s]{3,50}$"
        # reg = "^[A-Za-z0-9_]{3,100}$"
        reg = "^[A-Za-z0-9_ ]{3,100}$"
        
        if re.match(reg, field):
            return True
        return False
    
    @staticmethod
    def field_length_validator(text_type, text):
        if text_type in ['remarks', 'del_reason']:
            text_strip = str(text).strip()
            number_of_chars = len(text_strip)
            if (number_of_chars >= 3 and number_of_chars <= 200):
                return True
            return False
        elif text_type in ['vault_username', 'vault_password']:
            if len(str(text)) >= 1 and len(str(text)) <= 100:
                return True
            return False
        elif text_type in ['comment']:
            if len(str(text)) >= 3 and len(str(text)) <= 50:
                return True
            return False
        elif text_type in ['api_key']:
            if len(str(text)) >= 3 and len(str(text)) <= 40:
                return True
            return False
        elif text_type in ['rack_name']:
            if len(str(text)) >= 3 and len(str(text)) <= 100:
                return True
            return False

    @staticmethod
    def scheduler_name_validator(field):
        reg = "^[A-Za-z_]{3,50}$"
        if re.match(reg, field):
            return True
        return False

    @staticmethod
    def validate_frequency(freq, min_value, max_value):
        reg = '^[0-9]{1,2}(?:,[0-9]{1,2})*$'
        if freq == '*':
            return True
        elif(re.match(reg, freq)):
            frequencies = [int(x) for x in freq.split(',')]
            max_freq = max(frequencies)
            min_freq = min(frequencies)
            if (max_freq <= max_value and min_freq >= min_value):
                return True
            else:
                return False
        return False

    @staticmethod
    def delreason(reason):
        if len(reason) >= 3 and len(reason) <= 200:
            return True
        return False

    @staticmethod
    def mon_instance_validator(field):
        reg = "[ ]{10,20}$"
        if re.match(reg, field):
            return True
        return False
    
    @staticmethod
    def endpoint_validator(field):
        reg = "^[A-Za-z0-9_. \-/]{2,50}$"
        if re.match(reg, field):
            return True
        return False

    @staticmethod
    def phone_no(field):
        reg = r'^\+?1?\d{9,15}$'
        if re.match(reg, field):
            return True
        return False
    
    @staticmethod
    def city_name_validator(field):
        reg = "^[A-Za-z\s]{3,50}$"
        if re.match(reg, field):
            return True
        return False
    
    @staticmethod
    def rack_name_validator(field):
        reg = "^[A-Za-z0-9\s_-]{3,100}$"
        if re.match(reg, field):
            return True
        return False

    @staticmethod
    def instance_name_validator(field):
        reg = "^[A-Za-z0-9_]{3,50}$"
        if re.match(reg, field):
            return True
        return False
