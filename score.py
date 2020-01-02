"""
This module contains the Score, Alert and Alerts_List classes.
"""
from config import HEIGHT, WIDTH, SCORE_DURATION, SCORE_VELOCITY

class Score(object):
    """
    Keeps track of the game score, points required to reach the next level and
     a list of alerts which notify the player of points scored.
    score: integer points accumulated this game
    next_level_points: integer points required to reach the next level
    alerts: Alerts_List object to hold pop up score notifications
    """
    def __init__(self, nlp):
        """
        Receives an integer value for the points required to reach the next
         level. Sets the player's score to zero and score alerts to an empty
         list.
        """
        self.score = 0
        self.next_level_points = nlp
        self.alerts = Alerts_List()

    def __iadd__(self, rhs):
        """
        '+=' operator:
        Receives a single item or a list of items. The item may be an Alert
         object, or a tuple of the form ((x,y),pts).
        Alert objects are added to the alert list and pts are added to the
         player's score. The player can't score more points than those required
         to reach the next level. If the player loses points, the score can't be
         reduced below 0 points.
        """
        if type(rhs) is not list:
            rhs = [rhs]

        for alert in rhs:
            if type(alert) is tuple:
                alert = Alert(alert[0][0], alert[0][1], alert[1])

            p_max = self.next_level_points - self.score

            if alert.pts > p_max: # Scored more than next level threshold
                alert.pts = p_max
            elif -alert.pts > self.score: # Would take the player below zero pts
                alert.pts = -self.score

            self.score += alert.pts

            if alert.pts: # Don't create an alert for zero points
                self.alerts += alert

        return self

    def draw(self, screen):
        """
        Receives a PGZero screen object and the height and width of the game
         board.
        Draws the score and next level threshold in bottom left.
        Draws the score alerts
        """
        screen.draw.text(f'{self.score}/{self.next_level_points}',
                         bottomleft=(10, HEIGHT-10))
        self.alerts.draw(screen)

    def is_new_level(self):
        """
        Tests and reports player's progression to the next level.
        """
        if self.score >= self.next_level_points:
            return True

        return False

    def update(self, delta):
        """
        Given a time delta since the last update and the height of the game
         board, updates the score alert pop ups.
        """

        self.alerts.update(delta)

class Alerts_List(object):
    """
    Represents a list of Alert objects.
    """
    def __init__(self):
        self.contents = []

    def __str__(self):
        """
        Returns a formatted string for printing.
        """
        if self.contents:
            s = 'Alerts_List:\n'
            s += '     x pos     y pos       pts      life      vely\n'
            for a in self.contents:
                s += f'{a.x:10.2f}{a.y:10.2f}{a.pts:10}{a.life:10}{a.vely:10.2f}\n'
        else:
            s = 'Empty Alerts_List:\n'
        return s

    def __len__(self):
        return len(self.contents)

    def __iter__(self):
        return iter(self.contents)

    def __getitem__(self, key):
        return self.contents[key]

    def __setitem__(self, key, item):
        self.contents[key] = item

    def __delitem__(self, key):
        del self.contents[key]

    def __iadd__(self, rhs):
        """
        '+=' operator appends a single Alert object
        """
        self.contents.append(rhs)
        return self

    def draw(self, screen):
        """
        Given a PGZero screen object and the width of the game board, draws
         every alert in the list on the screen.
        """
        for a in self.contents:
            a.draw(screen)

    def update(self, delta):
        """
        Given the time in ms since the last update and the height of the game
         board, move each alert and delete the expired ones.
        """
        cnt = 0
        while cnt < len(self.contents):
            self.contents[cnt].move(delta)
            if self.contents[cnt].life < 0: # Time expired
                del self.contents[cnt]
            else:
                cnt += 1

class Alert(object):
    """
    Represents a single score notification which alerts player to newly scored
     points.
    x: float x position in pixels
    y: float y position in pixels
    pts: points scored in this alert
    life: time alert displays in ms
    vely: float y velocity in pix/ms
    """
    def __init__(self, x, y, pts):
        """
        Initializes the position, points, life and velocity of an alert.
        """
        self.x = x
        self.y = y
        self.pts = pts
        self.life = SCORE_DURATION * 1000 #convert to ms
        self.vely = SCORE_VELOCITY

    def __str__(self):
        """
        Returns a formatted string for printing the Alert.
        """
        atts = ['\t' + a + ': ' + str(v) for a,v in self.__dict__.items()]
        return type(self).__name__ + ' object:\n' + '\n'.join(atts)

    def draw(self, screen):
        """
        Given a PGZero screen object and the width of the board, draw this alert
         on the screen.
        """
        x, y, m = self.x, self.y, self.pts
        if x > WIDTH: #Off screen to right, adjust
            screen.draw.text(f'{m:+d}', midright=(WIDTH, y))
        elif x < 0: #Off screen to left, adjust
            screen.draw.text(f'{m:+d}', midleft=(0, y))
        else:
            screen.draw.text(f'{m:+d}', midtop=(x, y))

    def move(self, delta):
        """
        Given miliseconds since the last update and the height of the game
         board, deduct the time from the alert's life and move the alert up or
         down.
        """
        self.life -= delta # Decrement time to live
        if self.y > HEIGHT: # Move low alerts up on to screen
            self.y = HEIGHT-10
        elif self.y < 5: # Move high alerts down
            self.y = 5
            self.vely *= -1 # And make them float down instead of up
        self.y += self.vely*delta # Float up slowly