from datetime import datetime, timedelta
from calendar import monthrange
import calendar

class GenerateStats:

    def get_data(self, users, tagevent, chosenDateArray):
        data = []
        one_month = datetime.now() - timedelta(weeks=4)
        one_month_events = tagevent.query.filter(tagevent.timestamp > one_month).all()

        data.append(self.get_allGenderData(users))
        data.append(self.get_genderTagData(users, one_month_events))
        data.append(self.get_taginsByMonth(tagevent, chosenDateArray))
        data.append(self.get_ageData(users))
        data.append(self.get_taginsByDay(tagevent, chosenDateArray))#Send year and month
        data.append(self.get_taginsByHour(tagevent, chosenDateArray))#send year, month and day
        return data

    def get_allGenderData(self, users):
        maleCounter = 0
        femaleCounter = 0
        unknownCounter = 0

        for hit in users:

            js = hit.gender

            if js == "male":
                maleCounter += 1
            if js == "female":
                femaleCounter += 1
            if js == "unknown":
                unknownCounter += 1

        return [maleCounter, femaleCounter, unknownCounter]

    def get_genderTagData(self, users, one_month_events):
        maleCounter = 0
        femaleCounter = 0
        unknownCounter = 0

        for user in users:
            if user.gender == 'male':
                maleCounter += user.tagcounter
            elif user.gender == 'female':
                femaleCounter += user.tagcounter

        return [maleCounter, femaleCounter, unknownCounter]

    def get_taginsByMonth(self, event, chosenDateArray):
        yearArr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        currentYear = chosenDateArray['year']


        timestamps = event.query.filter(event.timestamp.contains(currentYear))

       # timestamps = event.query.all()

        for timestamp in timestamps:

            for x in range(1, 13):
                if x == timestamp.timestamp.month:
                    yearArr[x-1] += timestamp.amount

        yearArr.append(int(currentYear))
        return yearArr

    def get_taginsByDay(self, event, chosenDateArray):

        currentYear = chosenDateArray['year']
        currentMonth = chosenDateArray['month']

        datequery = currentYear + '-' + currentMonth

        uselessTuple = monthrange(int(currentYear), int(currentMonth))

        daysInMonth = uselessTuple[1]

        dayArr = [0]*daysInMonth

        timestamps = event.query.filter(event.timestamp.contains(datequery))

        for timestamp in timestamps:
            for x in range(1, daysInMonth+1):
                if x == timestamp.timestamp.day:
                    dayArr[x-1] += timestamp.amount

        return dayArr

    #Add optional parameter for user to be able to choose year, month and day
    def get_taginsByHour(self, event, chosenDateArray):
        currentYear = chosenDateArray['year']
        currentMonth = chosenDateArray['month']
        currentDay = chosenDateArray['day']

        datequery = currentYear + '-' + currentMonth + '-' + currentDay

        print(datequery)

        timestamps = event.query.filter(event.timestamp.contains(datequery))

        hourArr = [0]*24

        for timestamp in timestamps:
            for x in range(1, 25):
                if x == timestamp.clockstamp:
                    hourArr[x-1] += timestamp.amount

        return hourArr




    def get_ageData(self, users):
    #15-25
    #26-35
    #36-45
    #46-55
    #56-65
    #65+

        currentYear = int(self.get_current_year_string())
        ageArr = [0, 0, 0, 0, 0, 0]

    # a_string[:4]
        for user in users:

            #Riktiga medlemmar har 12-siffrigt pnummer.
            #Företag har 10-siffrigt. VIKTIGT!
            # "year" verkar inte finnas på user.birth_date.year. Hårdkodade in ett datum för att statistiksidan ska fungera! /Patrik
            temp_ssn = 0
            if len(user.ssn) == 8:
                temp_ssn = user.ssn[:-4]
                if int(temp_ssn[:-2]) == 19 or int(temp_ssn[:-2]) == 20:

                    age = currentYear - int(temp_ssn)

                    if age >= 15 and age <= 25:
                        ageArr[0] += 1
                    if age >= 26 and age <= 35:
                        ageArr[1] += 1
                    if age >= 36 and age <= 45:
                        ageArr[2] += 1
                    if age >= 46 and age <= 55:
                        ageArr[3] += 1
                    if age >= 56 and age <= 64:
                        ageArr[4] += 1
                    if age >= 65:
                        ageArr[5] += 1

        return ageArr

    def get_current_year_string(self):
         now = datetime.now()
         currentYear = str(now.year)

         return currentYear

    def get_current_month_string(self):
         now = datetime.now()
         currentMonth = str(now.month)

         return currentMonth

    def get_current_day_string(self):
        now = datetime.now()
        currentDay = str(now.day)

        return currentDay


''' if len(currentMonth) < 2:
fulHack = "-"
if int(currentMonth) < 10:
    fulHack += "0"

fulHack += currentMonth
fulHack += "-"'''
