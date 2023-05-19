# Future Enhancements

1. Currently entering an occupation requires 2 commands, for example:<br>
	`goto Amazon`<br>
	`enter Amazon`<br>
Expand the **enter** command to go to the occupation first (if not there already)<br>
**Note:** this should not be allowed when playing in production mode.<br>
Status: **ACTIVE**<br>
Change completed, but still need to restrict in production game mode.</p>

2. If a player is currently on an occupation entry square, allow the **enter**
command without an argument to enter that occupation.<br>
For example if I'm on square 13 (Amazon occupation entry) I can issue
`enter` instead of `enter Amazon`<br>
If the player is not on an Occupation entry square, return an error.<br>
Status: **OPEN**</p>

3. Implement a timed game type (i.e. a game that lasts a set number of minutes).<br>
It can be specified in GameRunner with **--type timed** command line argument,<br>
but the implementation is missing. Timer should start when the **start** command is executed,<br>
and checked at the end of each players turn (on the next command).
Status: **ACTIVE**</p>

4. The "end" command should declare a winner.<br>
Status: **OPEN**</p>

5. Jazz Age edition requires support for more than one specialProcessing entry.
RCA.json square #5 has two: lose all your cash, and go to Unemployment.
Changes to GameSquare and OccupationSquare.
Status: **OPEN**</p>

6. Add a player attribute that indicates the type of player: computer or human.<br>
The end goal is to use AI (neural network) to create a "smart" computer player<br>
by running thousands of games and feeding the results to the neural network.<br>
Status: **OPEN**</p>

7. Add Air Travel transportation squares.<br>
In Hi-Tech version change 2 of the Amtrak squares 12 and 35 to Airlines: LAX and ATL respectively.<br>
The rules are:<br>
Players landing on an Amtrak square advances to the next Amtrak station OR the closest Airline.<br>
Players landing on LAX advances to the nearest Amtrak station (square#22) OR to a connecting flight at ATL (square #35).<br>
Players landing on ATL advances to the nearest Amtrak station (square#3) OR to a connecting flight at LAX (square #12).<br>
The player rolls again after reaching their destination.<br>
Status: **OPEN** </p>

8. Implement bonus all. The bonus amount is applied to the player landing on the bonus square,<br>
and any players that are currently on  or have completed the associated career path.<br>
The current specialProcessing type is "bonus". Need to added a new type like "bonus_all".<br>
Status: **OPEN** </p>

---
## Turn Outcome
There needs to be a metric for assessing the outcome or quality of a player's turn.<br>
This is needed for future training an ANN for a computer player.<br>
The outcome then is a function of several different factors:
- Net point change
- Opportunity cards gained/lost
- Experience cards gained/lost
- Hospital stay (-1 or 0)
- Unemployment stay (-1 or 0)
- Degrees gained (1 or 0)
- Occupations completed (1 or 0)

Net point change is the number of points gained or lost in the turn and is the sum of<br>
delta cash (in 000's), delta Stars and delta Hearts.<br>

Cards gained/lost. The number of Experience/Opportunity cards gained or lost because  
of some penalty. For example, when another player calls in favors  
or when landing on "Buy Experience" and lose a card for "just looking."

Hospital/Unemployment stay. A net loss of 1 when a player is sent to the Hospital or Unemployment  
and each time the player remains there.  

Goal fulfillment. Has a value of -1, 0 or 1 for each goal component.  
A value of -1 if a previously fulfilled goal becomes short because of some loss (like half your cash).  
0 if no net change. 1 if the goal is fulfilled.

Defensive strategy. There are some defensive or strategic actions that contribute to the overall quality (outcome) of a turn.  
These include: 
- bumping another player, 
- backstabbing other player(s), 
- buying insurance to avoid penalties
- using an Opportunity card  
- using an Experience card

Some Opportunity cards are better (more valuable) than others, for example a move to any border square  
is better than advancing to an occupation and meets normal requirements.  
Consequently, the relative quality of each type of Opportunity card (there are 7 types)  
is included in the opportunityCards.json file.

The same argument can be made for Experience cards. Clearly a triple-wild card is more valuable than a fixed number of spaces card.  
The relative of each type of Experience card (there are 4 types) is included in the experienceCards.json file.

Occupation points is simply the sum of possible points available. That is, cash bonus in thousands + #stars + #hearts.  
This is set in the configuration section of the Occupation's/Career's JSON file.  
For example in the Software Engineering career possible points are $4,000 bonus (4 points), 22 Stars, 6 Hearts, total = 32 points  
Also there are 2 salary increases for $2,000 and times the roll of 1 die (avg. $3,000) for 5 points.

The value of this Career is relative to the players individual success formula. This career is then  
valuable for a player going for Stars, okay going for cash, and not so good if Hearts is your goal.  

Scenario 1: Formula = $40,000, 40 Stars, 20 Hearts = 100 total  
goal points/total points:                (0.4,   0.4,    0.2)
occupation ratios: (4/32, 22/32, 6/32) = (0.125, 0.6875, 0.1875)
differences: (-0.275, 0.2875, -0.0125)

Scenario 2: Formula = 40,000, 10 Stars, 50 Hearts  
goals/total points: (40/100, 10/100, 50/100) = (0.4, 0.1, 0.5)
differences: (-0.275, 0.5875, -0.3125)


Each of the above measures is multiplied by a weight that indicates its relative importance.<br>

So the outcome = <br>
(w1 x dPoints) + (w2 x dOpportunities) + (w3 x dExperiences) + <br>
(w4 x Hospital) + (w5 x Unemployment) + (w6 x degrees) + (w7 x occupations) + <br>
(w8 x net salary increase/decrease in thousands) + <br>
(w9 x ( cash goal fulfilled + Stars goal + Hearts goal) ) + <br>
(w10 x Opportunity card value) + (w11 x Experience card value) + <br>
(w12 x occupation points)

Cash points are measured in thousands of dollars. So $22,000 = 22 points.  
The weights are globally configurable by Edition in the rules.json file.  
Initial defaults are w1=2, w2,w3=1, w4,w5=4, w6,w7=2, w8=2, w9=3, w10,w11=1

**Sample turns**
Using Hi-Tech edition. Assume the player has $10,000 cash, 10 Stars, 20 Hearts and a $5,000 annual salary.  
1. Player lands on danger square in Aerospace Engineering (10 Stars but go to Hospital):  
outcome = 2 x 10 + 4 x -1 = 20 - 4 = 16</p>

2. Player in Patent Attorney lands on Salary up $4,000 and 12 Stars.  
outcome = (2 x 4) + (2 * 12) = 8 + 24 = 32</p>

3. Player lands on "Cut salary by 1/2" square.  
The player's salary/2 is $2,500 which is rounded up to $3,000 for a net loss of $2,000.  
outcome = 2 x -2 = -4 </p>

Obviously the player's goal - computer or human - is to maximize the outcome of each turn.  
The computer player's strategy is to determine the outcome of each possible move  
and select the one with the highest outcome.  


