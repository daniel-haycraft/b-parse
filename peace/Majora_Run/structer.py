class Append_to_csv(object):
    def __init__(self, li, fullname, name, addy, city, state, zip_):
        self.li = li 
        self.fullname = fullname
        self.name = name
        self.addy = addy
        self.city = city
        self.state = state
        self.zip_ = zip_
    def handle_the_update(li, fullname, name, addy, city, state, zip_):
        li["Full Name"] = fullname
        li["Name"] = name
        li["Address"] = addy
        li["City"] = city
        li["State"] = state
        li["Zip"] = zip_