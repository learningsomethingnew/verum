from splinter import Browser
import re
import csv

class MemberVoteHistory():
    def __init__(self, links):
        executable_path = {
            'executable_path': '/Users/someone/Documents/Dev/Verum/Scrapper/chromedriver'
        }
        self.b = Browser('chrome', **executable_path)
        self.start_range = 1
        #DOES NOT TAKE INTO ACCOUNT MULTIPLE READINGS MUST ADDRESS
        #{BILL_ID: {LEG_BRANCH: {AYE:[REP_ID], NO:[REP_ID], NV:[REP_ID], EA:[REP_ID]}}
        self.voting_data = []
        self.rep_vote = []
        #BILL_ID = YEAR_RCS#
        #{BILL_ID: {RCS#, DOC_NAME, TIMESTAMP, TOT_AYE, TOT_NO, TOT_NV, TOT_EA, TOT_VOTE, RESULT]}
        self.bill_info = []

        #{REP_ID: ARRAY = NAME, LEG_BRANCH, PARTY, DISTRICT}
        self.rep_info = []


        #Regex Patterns
        self.URL_PATTERN = "sSession=([1-3][0-9]{3}\w\d|[1-3][0-9]{3})&sChamber=(\w){1}&nUserID=(\d+)"
        self.NAME_PATTERN = "Vote History: Representative (\w+, \w|\w+-\w+|\w+)"
        self.DISTRICT_PATTERN = "District (\d+)"
        self.EXTRA_SESSION_PATTERN = "(\d+) (\w+)"
        self.YEAR_SESSION_PATTERN = "([1-3][0-9]{3})-([1-3][0-9]{3})"
        self.MOTION_PATTERN = "(A\d|Motion \d+|Suspend Rules|R\d+|M\d+|C RPT)"
        self.READING_PATTERN ="(2nd Reading|Second Reading|Third Reading|3rd Reading)"
        self.MOTION_NAME_PATTERN = "A\d+ (\w+, \w.|\w+)" #Assumes A only
        #Dict of lookup words to convert words like 'First' to 1
        self.word_to_num = {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5,
            "sixth": 6,
            "seventh": 7,
            "eighth": 8,
            "ninth": 9,
            "tenth": 10,
        }

        self.vote_to_num = {
            "Aye": 1,
            "No": 2,
            "N/V": 3,
            "Excused Absence": 4,
        }

        self.readings = {
            '2nd Reading': 2,
            'Second Reading': 2,
            'Third Reading': 3,
            '3rd Reading': 3,
        }

        for link in links:
            self.iterate_through_rep_links(link)
        self.b.quit()

    def iterate_through_rep_links(self, link):
        #Link is starting point of that years vote records
        self.b.visit(link)
        num_reps = self.count_num_of_reps() +1
        session = self.b.find_by_xpath("""//*[@id="mainBody"]/div[3]""").value
        session_id = ''
        #Loop that rolls through the list of candidates and calls the actions for data pulling
        for x in range(self.start_range,num_reps):
            result = self.b.find_by_xpath("""//*[@id="mainBody"]/ul/li[{}]/a""".format(x))
            #Navigate to the result
            print("SESSION", session, " NAME ", result.value)
            result.click()

            if self.test_for_unavailable_data():
                session_id = self.get_data()
                #navigate back and rerun on next result
                self.b.back()
            else:
                self.b.back()

        #save the data by session
        self.save_results(session_id)

    def test_for_unavailable_data(self):
        vote_data = self.b.find_by_text("""
        Vote data is unavailable.
							""")
        #If the text isn't found on the site, return True
        if len(vote_data) == 0:
            return True

        #Rep has not voting data
        else:
            session_id, chamber, rep_id, short_name, district = self.get_session_chamber_repid_name_district()
            self.rep_info.append([rep_id, session_id, chamber, short_name, district])
            return False

    def get_data(self):
        """
        Reviews voting data. Skips the first row as that is the headers
        :return:
        """
        session_id, chamber, rep_id, short_name, district = self.get_session_chamber_repid_name_district()
        row = 2
        while True:
            #grab rcs
            rcs_find = self.b.find_by_xpath("""//*[@id="mainBody"]/table/tbody/tr[{}]/td[1]""".format(row))
            #Testing to see if we are at the end of the list
            if len(rcs_find) != 0:
                rcs = rcs_find.value

                #Bill Name & Link
                doc, doc_link = self.get_doc_information(row)

                #Parsing Subject/Motion
                reading, subject, motion, motion_name, title, motion_text = self.get_subject_motion(row)

                #TIMESTAMP OF VOTE
                timestamp = self.b.find_by_xpath("""//*[@id="mainBody"]/table/tbody/tr[{}]/td[4]""".format(row)).value

                #REPRESENTATIVE VOTE
                vote = self.b.find_by_xpath("""//*[@id="mainBody"]/table/tbody/tr[{}]/td[5]""".format(row)).value

                #PASS
                result = self.b.find_by_xpath("""//*[@id="mainBody"]/table/tbody/tr[{}]/td[12]""".format(row)).value

                bill_id = session_id+'_'+rcs
                self.rep_info.append([rep_id, session_id, chamber, short_name, district])

                self.rep_vote.append([rep_id, session_id, bill_id, vote, timestamp, reading, motion, motion_name, result, title, motion_text])
                #intended to be parsed down to unique ID's. Bill history will have the detailed information
                self.bill_info.append([bill_id, chamber, session_id, doc, doc_link, title, timestamp, motion_text])
            else:
                break
            row += 1
        return session_id


    def get_subject_motion(self, row):
        # SUBJECT/MOTION
        full_subject = self.b.find_by_xpath("""//*[@id="mainBody"]/table/tbody/tr[{}]/td[3]""".format(row)).value
        #if multiline subject
        subject = full_subject.splitlines()
        reading = 1
        motion = ''
        motion_name = ''
        title = ''
        motion_text = ''
        #If subject is multiple lines, then process second line. First line is the subject
        if len(subject) > 1:
            title = subject[0]
            motion_text = subject[1]
            #find number of readings. Search doesn't have a len. If it fails finding reading, reading = 1
            try:
                reading_search = re.search(self.READING_PATTERN, subject[1]).group(0)
                if reading_search in self.readings:
                    reading = self.readings[reading_search]
            except:
                reading = 1
            try:
                motion = re.search(self.MOTION_PATTERN, subject[1]).group(0)
            except:
                motion = ''

            try:
                motion_name = re.search(self.MOTION_NAME_PATTERN, subject[1]).group(0)
            except:
                motion_name = ''
        return reading, subject, motion, motion_name, title, motion_text

    def get_doc_information(self, row):
        # DOC INFORMATION
        doc_find = self.b.find_by_xpath("""//*[@id="mainBody"]/table/tbody/tr[{}]/td[2]/a""".format(row))
        if len(doc_find) != 0:
            doc = doc_find.value
            doc_link = doc_find['href']
        else:
            doc = ''
            doc_link = ''
        return doc, doc_link

    def get_session_chamber_repid_name_district(self):
        matches = re.search(self.URL_PATTERN, self.b.url)
        session_id = matches.group(1)
        chamber = matches.group(2)
        rep_id = matches.group(3)
        try:
            title = self.b.find_by_xpath("""//*[@id="title"]""").value
            short_name = re.search(self.NAME_PATTERN, title).group(1)
            district = re.search(self.DISTRICT_PATTERN, title).group(1)
        except:
            #If there is no voter data available, fill with empty strings
            title = ''
            short_name = ''
            district = ''

        return session_id, chamber, rep_id, short_name, district


    def get_session(self, xpath_term):
        """

        :param xpath_term: String containing the session year of the candidates vote
        :return:
        """
        if "Extra Session" in xpath_term:
            session_search = re.search(self.EXTRA_SESSION_PATTERN, xpath_term)
            start_term = session_search.group(1)
            end_term = session_search.group(1)
            extra_session = self.word_to_num[session_search.group(2).lower()]

        else:
            session_search = re.search(self.YEAR_SESSION_PATTERN, xpath_term)
            start_term = session_search.group(1)
            end_term = session_search.group(2)
            extra_session = 0

        return end_term, extra_session, start_term


    def count_num_of_reps(self):
        """
        Using http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2015E5&sChamber=H as template
        this function will count the number of items in the ul so that we know how many reps to cycle through
        :return: INT of number of LIs
        """
        return self.b.evaluate_script("""document.evaluate('count(//*[@id="mainBody"]/ul/li)', document, null, XPathResult.ANY_TYPE, null).numberValue""")


    def save_results(self, session_id):
        with open("rep_info_{}.csv".format(session_id), "a") as f:
            writer = csv.writer(f)
            for row in self.rep_info:
                writer.writerow(row)
        with open("rep_vote_{}.csv".format(session_id), "a") as f:
            writer = csv.writer(f)
            for row in self.rep_vote:
                writer.writerow(row)
        with open("bill_info_{}.csv".format(session_id), "a") as f:
            writer = csv.writer(f)
            for row in self.bill_info:
                writer.writerow(row)

if __name__ == "__main__":
    links = ['http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2015&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2015E2&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2007E2&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2015E1&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2013&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2011&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2009&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2007&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2007E1&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2005&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2003E3&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2003&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2003E2&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2003E1&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2001&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2001E1&sChamber=H']
    mvh = MemberVoteHistory(links)