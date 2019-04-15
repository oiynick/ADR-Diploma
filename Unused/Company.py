class Company:

    def __init__(self, hr, maxmark, maxmarkt):
        self.hr_cost = hr   # TODO: bring the model
        self.mark_cost = 0   # TODO: bring the model
        self.sales_cost = 0   # TODO: bring the model
        self.maxmark = maxmark
        self.maxmarkt = maxmarkt

    def __getitem__(self, index: int):
        return self.hr_cost*index + self.com_cost*index
