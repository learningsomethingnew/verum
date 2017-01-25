from splinter import Browser
import re
import csv
import time

class VoterStats():
    def __init__(self, links):
        executable_path = {
            'executable_path': '/Users/someone/Documents/Dev/Verum/Scrapper/chromedriver'
        }
        self.b = Browser('chrome', **executable_path)


        #Regex Patterns
        self.URL_PATTERN = "sSession=([1-3][0-9]{3}\w\d|[1-3][0-9]{3})&sChamber=(\w){1}"
        self.EXTRA_SESSION_PATTERN = "(\d+) (\w+)"
        self.YEAR_SESSION_PATTERN = "([1-3][0-9]{3})-([1-3][0-9]{3})"
        self.PARTY_PATTERN = "(R|D|U|I)"
        #general information
        self.session_id = ''
        self.chamber = ''
        self.rep = [
            ['SESSION_ID',
             'CHAMBER',
             'USER_ID',
             'DISTRICT',
             'NAME',
             'PARTY',
             'TOTAL_VOTES',
             'ELIGIBLE_VOTES',
             'ACTUAL_VOTES',
             'VOTE_PER',
             'WITH_MAJORITY',
             'WITH_MAJORITY_PER',
             'AGAINST_MAJORITY',
             'AGAINST_MAJORITY_PER']
        ]
        for item in links:
            self.main(item)
            print(item)
        self.save_results()
        self.b.quit()

    def main(self, link):
        start = time.time()
        self.b.visit(link)
        num_reps = self.get_num_of_reps()
        row = 2
        sess_id, chamber = self.get_session_chamber_repid()
        while row < num_reps:
            district = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[1]""".format(row)).value
            name_party = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[2]""".format(row)).value
            party = name_party[len(name_party)-2:len(name_party)-1]
            name = name_party[:len(name_party)-4]
            tot_vote = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[3]""".format(row)).value
            eli_vote = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[4]""".format(row)).value
            act_vote = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[5]""".format(row)).value
            vote_per = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[6]""".format(row)).value
            w_maj = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[7]""".format(row)).value
            w_maj_per = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[8]""".format(row)).value
            against_maj = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[9]""".format(row)).value
            against_maj_per = self.b.find_by_xpath("""//*[@id="mainBody"]/table[1]/tbody/tr[{}]/td[10]""".format(row)).value
            self.rep.append([sess_id, chamber, '', district, name, party, tot_vote, eli_vote, act_vote, vote_per, w_maj, w_maj_per, against_maj, against_maj_per])
            row +=1
        end = time.time()
        print(end-start)

    def get_session_chamber_repid(self):
        matches = re.search(self.URL_PATTERN, self.b.url)
        session_id = matches.group(1)
        chamber = matches.group(2)
        return session_id, chamber

    def save_results(self):
        with open("repfile.csv", "a") as f:
            writer = csv.writer(f)
            for row in self.rep:
                writer.writerow(row)

    def get_num_of_reps(self):
        """
        Using http://www.ncleg.net/gascripts/voteHistory/MemberVoteHistory.pl?sSession=2015E5&sChamber=H as template
        this function will count the number of items in the ul so that we know how many reps to cycle through
        :return: INT of number of LIs
        """
        return self.b.evaluate_script("""document.evaluate('count(//*[@id="mainBody"]/table[1]/tbody/tr)', document, null, XPathResult.ANY_TYPE, null).numberValue""")

if __name__ == "__main__":

    links = ['http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E5&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E4&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E3&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E2&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2007E2&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E1&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2013&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2011&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2009&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2007&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2007E1&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2005&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2003E3&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2003&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2003E2&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2003E1&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2001&sChamber=H','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2001E1&sChamber=H', 'http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E5&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E4&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E3&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E2&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2015E1&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2013&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2011&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2009&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2007&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2007E1&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2005&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2003E3&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2003&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2003E2&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2003E1&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2001&sChamber=S','http://www.ncleg.net/gascripts/voteHistory/MemberVoteStatistics.pl?sSession=2001E1&sChamber=S']
    vs = VoterStats(links)