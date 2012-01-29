from datetime import date, timedelta

class Space(models.Model):
    """
    <space>
        <id>c5lQB2YXqr2PaFaaeP0Qfc</id>
        <description>Assembla Space</description>
        <name>Assembla</name>
    </space>
    """
    assembla_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=False,
        help_text='Harvest data for and display on the front data.')

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return 'walrus:space', [self.slug]

    def tickets_without_milestone(self):
        return self.tickets.filter(milestone__isnull=True)

    def active_statuses(self):
        return self.statuses.exclude(
            name__in=('Fixed', 'Invalid',)
        )

    def new_status(self):
        return self.statuses.get(name='New')

    def test_statuses(self):
        return self.statuses.filter(
            name__in=('Test', 'Code review',)
        )

    def active_milestones(self):
        return self.milestones.filter(is_active=True)


class Milestone(models.Model):
    """
    <milestone>
        <id type="integer">15</id>
        <title>My release</title>
        <description>Hello world description</description>
        <due-date type="date" nil="true"></due-date>
        <is-completed type="boolean">false</is-completed>
        <space-id>at6CkKLwSr34lqacjKAZfO</space-id>
    </milestone>
    """
    assembla_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField()
    space = models.ForeignKey(Space, related_name='milestones')
    is_active = models.BooleanField(default=False,
        help_text='Harvest data for and display on the front data.')

    class Meta():
        ordering = ['-due_date',]

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return 'walrus:milestone', [self.space.slug, self.slug]

    def claimed_points(self):
        """
        Returns the current total estimate for all of the milestone's
        tickets which have been completed.
        """
        return sum([ticket.estimate for ticket in self.completed_tickets()])

    def unclaimed_points(self):
        """
        Returns the current total estimate for all of the milestone's
        tickets which are still active.
        """
        return sum([ticket.estimate for ticket in self.active_tickets()])

    def total_points(self):
        """
        Returns the current total estimate for the milestone.
        """
        return sum([ticket.estimate for ticket in self.tickets.all()])

    def active_tickets(self):
        """
        Returns all of the milestone's tickets which are active and
        incomplete.
        """
        active_tickets = filter(
            lambda ticket: ticket.status() in self.space.active_statuses(),
            self.tickets.all()
        )
        return self.tickets.filter(id__in=[ticket.id for ticket in active_tickets])

    def testable_tickets(self):
        """
        Returns all of the milestone's tickets which have been indicated
        to be testable.
        """
        testable_tickets = filter(
            lambda ticket: ticket.status() in self.space.test_statuses(),
            self.tickets.all()
        )
        return self.tickets.filter(id__in=[ticket.id for ticket in testable_tickets])


    def completed_tickets(self):
        """
        Returns all of the milestone's tickets which are complete.
        """
        return self.tickets.exclude(
            id__in=[ticket.id for ticket in self.active_tickets()]
        )

    def latest_historical_date(self):
        """
        Returns the latest date during which this milestone had any
        changes to its tickets happen.
        """
        return TicketHistory.objects.filter(
            ticket__in=self.tickets.all()
        )[0].datetime

    def total_points_on_date(self, date):
        """
        Return the total points occurring for the milestone on :date.
        This travels from :date backwards in time and gets all tickets that
        existed before or at that time and calculates the total estimate
        of them all.
        """
        timestamp = set_to_end_of_day(date)
        history = TicketHistory.objects.filter(datetime__lte=timestamp)
        tickets = set([ticket_history.ticket for ticket_history in history
                       if ticket_history.ticket.milestone == self])
        return sum([ticket.estimate for ticket in tickets])

    def tickets_by_date(self, timestamp):
        """
        Get the tickets which had some history change before :timestamp.
        """
        # Get the tickets which had some history change before :timestamp.
        return self.tickets.all()\
            .filter(history__datetime__lte=timestamp)\
            .distinct()

    def active_points_on_date(self, timestamp):
        """
        Return the total points of all tickets that were set to
        no longer be active on or before :timestamp occurred.
        """
        timestamp = set_to_end_of_day(timestamp)
        tickets = filter(
            lambda ticket: ticket.state_on_date(timestamp) in self.space.active_statuses(),
            self.tickets_by_date(timestamp)
        )
        return sum([ticket.estimate for ticket in tickets])

    def completed_points_on_date(self, timestamp):
        """
        Return the total points of all tickets that were set to
        no longer be active on or before :timestamp occurred.
        """
        timestamp = set_to_end_of_day(timestamp)
        tickets = filter(
            lambda ticket: ticket.state_on_date(timestamp) not in self.space.active_statuses(),
            self.tickets_by_date(timestamp)
        )
        return sum([ticket.estimate for ticket in tickets])

    def points_in_test_on_date(self, timestamp):
        """
        Return the total points of all tickets that were set to test
        on or before :timestamp occurred.
        """
        timestamp = set_to_end_of_day(timestamp)
        tickets = filter(
            lambda ticket: ticket.state_on_date(timestamp) in self.space.test_statuses(),
            self.tickets_by_date(timestamp)
        )
        return sum([ticket.estimate for ticket in tickets])

    def total_points_in_date_range(self, start_date, end_date):
        """
        Return the total points occurring for the milestone during the
        time between :start_date and :end_date.
        """
        start_date = set_to_start_of_day(start_date)
        end_date = set_to_end_of_day(end_date)
        history = TicketHistory.objects.filter(
            datetime__lte=end_date,
            datetime__gte=start_date,
            ticket__milestone=self,
        )
        tickets = set([ticket_history.ticket for ticket_history in history])
        return sum([ticket.estimate for ticket in tickets])

    def burndown_data(self, start_date=None, range_in_days=14):
        """
        Generates and returns a dict representing the data
        for a burndown graph corresponding to the milestone.
        The data ranges from :start_date forward to a date
        denoted by :range, which is measurable in days.

        :start_date is a date object representing the start of
            the burndown's data period.
        :range_in_days is an positive integer representing the period in
            days that the data should cover.
        """
        if not start_date:
            if self.start_date:
                start_date = self.start_date
                latest_historical_date = convert_datetime_to_date(self.latest_historical_date())
                if self.due_date and self.due_date > latest_historical_date:
                    range_in_days = (self.due_date - self.start_date).days
                else:
                    range_in_days = (latest_historical_date - self.start_date).days
            else:
                # Set the end of the range to the last date that something happened.
                end_date = self.latest_historical_date()
                start_date = end_date+timedelta(days=range_in_days*-1)
        one_day = timedelta(days=1)
        if self.start_date and self.due_date:
            expected_range = (self.due_date - self.start_date).days
        else:
            expected_range = range_in_days
        timestamp = start_date
        # Maybe replace with a scan to find the highest of the remaining_points vars?
        total_points_in_milestone = self.active_points_on_date(start_date)
        data = []
        for i in xrange(range_in_days+1):
            remaining_points = self.active_points_on_date(timestamp)
            test_points = remaining_points - self.points_in_test_on_date(timestamp)
            # Calculate the expected points for the date.
            if i == 0:
                expected_points = total_points_in_milestone
            elif i == range_in_days:
                expected_points = 0
            else:
                expected_points = int(total_points_in_milestone - (i * float(total_points_in_milestone) / float(expected_range)))
                if expected_points < 0:
                    expected_points = 0
            data.append({
                'timestamp': timestamp.strftime('%d/%m'),
                'remaining_points': remaining_points,
                'test_points': test_points,
                'expected_points': expected_points,
            })
            timestamp = timestamp + one_day
        return data

class User(models.Model):
    """
    <user>
         <id>aRIULIPCWr2Oq0aaeP0Qfc</id>
         <login_name>andy</login_name>
    </user>
    """
    assembla_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Ticket(models.Model):
    """
    <ticket>
        <assigned-to-id></assigned-to-id>
        <description>This is the ticket description</description>
        <milestone-id type="integer"></milestone-id>
        <number type="integer">1</number>
        <priority type="integer">3</priority>
        <space-id>space_id</space-id>
        <status-name>New</status-name>
        <summary>This is the summary</summary>
        <working_hour type="float">4.0</working_hour>
    </ticket>
    """
    number = models.IntegerField()
    description = models.TextField(blank=True)
    summary = models.CharField(max_length=255)
    priority = models.IntegerField()
    estimate = models.IntegerField()
    space = models.ForeignKey(Space, related_name='tickets')
    assigned_to = models.ForeignKey(User, related_name='tickets',
                                          blank=True, null=True)
    milestone = models.ForeignKey(Milestone, related_name='tickets',
                                          blank=True, null=True)

    def __unicode__(self):
        return u'#{0} - {1}'.format(self.number, self.summary)

    def status(self):
        return self.history.all()[0].status

    @permalink
    def get_absolute_url(self):
        if self.milestone:
            return 'walrus:ticket', [self.space.slug, self.milestone.slug, self.number]
        else:
            return 'walrus:ticket', [self.space.slug, None, self.number]

    def state_on_date(self, timestamp):
        """
        Return the tickets state at the end of the day denoted
        by :timestamp.
        """
        timestamp = set_to_end_of_day(timestamp)
        return self.history.filter(
            datetime__lte=timestamp
        )[0].status


class TicketStatus(models.Model):
    """
    <ticket-status>
        <name>New</name>
    </ticket-status>
    """
    space = models.ForeignKey('Space', related_name='statuses')
    name = models.CharField(max_length=25)

    class Meta():
        verbose_name_plural = 'ticket statuses'

    def __unicode__(self):
        return self.name


class TicketHistory(models.Model):
    """
    <comment>
        <comment>
            we need: 1. two column page template to match the wireframe 2. javascript that transforms links to testimonials to make them load ajaxically into a popup window 3. javascript to load the content, and grab the div that contains the content we need (probably need to add that div to the new template), and puts it into the popup window. - this does something similar: http://www.abacussolutions.com.au/ - this might be useful, but looking a bit old now: http://www.abacussolutions.com.au/media/js/jquery.ajaxify_contents.js
        </comment>
        <rendered type="boolean">false</rendered>
        <created-on type="datetime">2011-10-26T11:13:08+11:00</created-on>
        <updated-at type="datetime">2011-10-26T11:13:08+11:00</updated-at>
        <ticket-id type="integer">7606543</ticket-id>
        <user-id>di0DGS4Z8r3inTabIlDkbG</user-id>
        <ticket-changes>--- - - assigned_to_id - aweakley - mfinger</ticket-changes>
        <user>
            <id>di0DGS4Z8r3inTabIlDkbG</id>
            <login>aweakley</login>
            <login_name warning="deprecated">aweakley</login_name>
            <name>Alastair Weakley</name>
            <email>aweakley@gmail.com</email>
            <organization/>
            <website/>
        </user>
    </comment>
    """
    ticket = models.ForeignKey('Ticket', related_name='history')
    datetime = models.DateTimeField()
    status = models.ForeignKey('TicketStatus', related_name='ticket_histories')

    class Meta():
        ordering = ['-datetime',]
        verbose_name_plural = 'ticket histories'

    def __unicode__(self):
        return u'#{0} - {1}'.format(self.ticket.number, self.status)