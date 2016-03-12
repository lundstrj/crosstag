from server_helper_scripts.strip_ssn import strip_ssn
from server_helper_scripts.get_gender_from_ssn import get_gender_from_ssn
from crosstag_init import db
from db_models.user import User


# Updating an existing user in local DB from fortnox.
def update_user_in_local_db_from_fortnox(customer):
    user = User.query.filter_by(fortnox_id=customer['FortnoxID']).first()
    if user is None:
        return "she wrote upon it; no such number, no such zone"
    else:
        user.name = customer['Name']
        user.email = customer['Email']
        user.phone = customer['Phone']
        user.address = customer['Address1']
        user.address2 = customer['Address2']
        user.city = customer['City']
        user.zip_code = customer['Zipcode']
        user.gender = get_gender_from_ssn(customer)
        user.ssn = strip_ssn(customer)
        user.expiry_date = user.expiry_date
        user.create_date = user.create_date
        user.tag_id = user.tag_id
        if(user.tagcounter is None):
            user.tagcounter = 0
        if user.status is None:
            user.status = 'Inactive'

        db.session.commit()
