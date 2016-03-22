from datetime import datetime, timedelta
from calendar import monthrange


class GenerateStats:

    def get_data(self, users, tagevent, chosen_date_array):
        data = []
        one_month = datetime.now() - timedelta(weeks=4)
        one_month_events = tagevent.query.filter(tagevent.timestamp > one_month).all()

        data.append(self.get_all_gender_data(users))
        data.append(self.get_gender_tag_data(users, one_month_events))
        data.append(self.get_tagins_by_month(tagevent, chosen_date_array))
        data.append(self.get_age_data(users))
        # Send year and month
        data.append(self.get_tagins_by_day(tagevent, chosen_date_array))
        # Send year, month and day
        data.append(self.get_tagins_by_hour(tagevent, chosen_date_array))
        return data

    def get_all_gender_data(self, users):
        male_counter = 0
        female_counter = 0
        unknown_counter = 0

        for hit in users:

            js = hit.gender

            if js == "male":
                male_counter += 1
            if js == "female":
                female_counter += 1
            if js == "unknown":
                unknown_counter += 1

        return [male_counter, female_counter, unknown_counter]

    def get_gender_tag_data(self, users, one_month_events):
        male_counter = 0
        female_counter = 0
        unknown_counter = 0

        for user in users:
            if user.gender == 'male':
                male_counter += user.tagcounter
            elif user.gender == 'female':
                female_counter += user.tagcounter

        return [male_counter, female_counter, unknown_counter]

    def get_tagins_by_month(self, event, chosen_date_array):
        year_arr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        current_year = chosen_date_array['year']

        timestamps = event.query.filter(event.timestamp.contains(current_year))

        for timestamp in timestamps:
            for x in range(1, 13):
                if x == timestamp.timestamp.month:
                    year_arr[x-1] += timestamp.amount

        year_arr.append(int(current_year))
        return year_arr

    def get_tagins_by_day(self, event, chosen_date_array):

        current_year = chosen_date_array['year']
        current_month = chosen_date_array['month']

        date_query = current_year + '-' + current_month

        useless_tuple = monthrange(int(current_year), int(current_month))

        days_in_month = useless_tuple[1]

        day_arr = [0]*days_in_month

        timestamps = event.query.filter(event.timestamp.contains(date_query))

        for timestamp in timestamps:
            for x in range(1, days_in_month+1):
                if x == timestamp.timestamp.day:
                    day_arr[x-1] += timestamp.amount

        return day_arr

    # Add optional parameter for user to be able to choose year, month and day
    def get_tagins_by_hour(self, event, chosen_date_array):
        current_year = chosen_date_array['year']
        current_month = chosen_date_array['month']
        current_day = chosen_date_array['day']

        date_query = current_year + '-' + current_month + '-' + current_day

        print(date_query)

        timestamps = event.query.filter(event.timestamp.contains(date_query))

        hour_arr = [0]*24

        for timestamp in timestamps:
            for x in range(1, 25):
                if x == timestamp.clockstamp:
                    hour_arr[x-1] += timestamp.amount

        return hour_arr

    def get_age_data(self, users):
        # 15-25
        # 26-35
        # 36-45
        # 46-55
        # 56-65
        # 65+

        current_year = int(self.get_current_year_string())
        age_arr = [0, 0, 0, 0, 0, 0]

        for user in users:
            temp_ssn = 0
            if len(user.ssn) == 8:
                temp_ssn = user.ssn[:-4]
                if int(temp_ssn[:-2]) == 19 or int(temp_ssn[:-2]) == 20:
                    age = current_year - int(temp_ssn)
                    if age >= 15 and age <= 25:
                        age_arr[0] += 1
                    if age >= 26 and age <= 35:
                        age_arr[1] += 1
                    if age >= 36 and age <= 45:
                        age_arr[2] += 1
                    if age >= 46 and age <= 55:
                        age_arr[3] += 1
                    if age >= 56 and age <= 64:
                        age_arr[4] += 1
                    if age >= 65:
                        age_arr[5] += 1

        return age_arr

    def get_current_year_string(self):
        now = datetime.now()
        current_year = str(now.year)

        return current_year

    def get_current_month_string(self):
        now = datetime.now()
        current_month = str(now.month)

        return current_month

    def get_current_day_string(self):
        now = datetime.now()
        current_day = str(now.day)

        return current_day
