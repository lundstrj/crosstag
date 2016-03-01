def get_gender_from_ssn(customer):
    ssn_gender_number = customer['OrganisationNumber'][-2:]

    try:
        gender_number = int(ssn_gender_number[:1])
        if gender_number % 2 == 0:
            return 'female'
        elif int(gender_number) % 2 == 1:
            return 'male'
        else:
            return 'unknown'
    except:
        return None
