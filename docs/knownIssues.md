# Known Issues and Future Enhancements

---
## Known Issues
1. When resolving take_shortcut the player needs to roll or use an experience<br>
from the next_square. Currently it just goes to the next_square and executes it.<br>
Status: **COMPLETE**<br>
"resolve take_shortcut yes" sets the player's board location to the space<br>
 BEFORE the next_square in the shortcut specialProcessing.<br>
 This worked for UF but not for Pfizer because the square numbering is not consecutive.<br>
 To fix this, and keep the logic the same as UF, I updated the Pfizer occupation JSON<br>
 file in the Hi-Tech and UK versions. The Hi-Tech board image and Visio model also update
 for Hi-Tech, but not for UK. See issue #9 below. New template file: "Careers Template Hi-Tech 3.0"</p>

2. The resolve select_degree command gets a syntax error on multi-word degree names:<br>
Business Admin, Computer Science. <br>
Change to single word: BusinessAdmin, ComputerScience OR concat the arguments into a single string.<br>
Status: **COMPLETE**<br>
Change to parse_command_string to concatenate the resolve arguments
into a single string, for example:<br> `resolve("select_degree","Computer Science" )`</p>

3. If player 1 enters an Occupation and rolls (so they're on the Occupation path),
if player 2 lands on that occupation's entry square, the can_bump<br>
logic mistakenly adds player 1 to player 2's can_bump list.<br>
See `CareersGameEngine.who_occupies_my_square()` to fix.<br>
Status: **COMPLETE**</p>

4. The following commands should not be allowed when playing in production mode:
goto, advance, add_degree, enter <occupation> when not on the target occupation entrance square<br>
The 'goto', 'add_degree' and 'advance' commands are blocked in GameRunner because<br>
they are also used internally. For testing in production mode use the GameRunner
command line argument --params test_mode. This loads the prod parameters, but allows those 3 commands.<br>
Status: **COMPLETE**</p>

5. The perform command does not execute the perform string - the result
message is the JSON formatted command, but it's not executed.<br>
For example "perform roll 2" result message for player DWB is {"player": "DWB", "roll": 6, "dice": [3, 3]}<br>
The the "roll" isn't executed and so the player doesn't move.<br>
Also pending action(s) are not automatically resolved as described in the method comments.<br>
Status: **OPEN**</p>

6. Resolving select_degree with a missing or invalid degree program<br>
incorrectly clears the PendingActionType.SELECT_DEGREE pending action.<br>
Status: **INVESTIGATING**<br>
Problem is add_degree returns an error so the statement<br>
`if result.is_successful() and not player.on_holiday:`<br>
is False resulting in all pending actions being cleared.</p>

7. If a player lands on space 2 of Google (Pay $2000 OR go on Unemployment) and is unable to pay<br>
or elects not to pay, the player is sent to Unemployment but in passing Payday, collects<br>
their salary. This is wrong - the player should go directly to Unemployment and not go around the board to get there.<br>
Same problem with landing on an occupation square that sends you to the Hospital.<br>
Status: **COMPLETE**<br>
This was also a problem in Lister & Bacon, square 0.<br>
The CareersGameEngine._goto(...)  checks the destination border_square.name 
and if Unemployment or Hosiptal does not execute pass_payday </p>

8. If a player gets an error when resolving choose_occupation (by specifying College instead of <br>
an Occupation or specifying an Occupation that doesn't exist) the pending action
is cleared incorrectly.<br>
Status: **OPEN**</p>

9. Update the UK version Visio model and board image with the revised Pfizer UK JSON.<br>
Status: **COMPLETE**<br>
New template file: "Careers Template UK London 2.0"</p>

10. The number of turns (for a player) should not be incremented for query commands,
only roll, use experience and use opportunity.<br>
Status: **INVESTIGATING**

11. The logic for determining a winner in a points or timed game is wrong.
Status: **ACTIVE** Winner of a points game and timed game for multiple players is complete.<br>
For single player timed game, the elapsed game time is not checked unless the player issues a "next" command.<br>
The output format is "The game is over, the winner is DWB with 55 points.Game time: 11"<br>
Should add the points for all the players and add "minutes" after the game time.

12. The command for using opportunity card 16: GOLDEN  OPPORTUNITY to join the Company of your choice. Meet Normal Requirements<br>
is "use opportunity 16 UF" for example, where UF here is the occupation of choice.<br>
This takes the player to the chosen opportunity (via a goto command) but then immediately<br>
goes to a different border square. In this case I got:</p>
  Advance to  UF<br>
  DWB landed on UF  (7)<br>
  DWB landed on ESPN  (15)</p>
The problem is it automatically does a "roll" which is correct,<br>
but advances to a border square instead of an occupation square.<br>
In this case it rolled an 8 which went to square 15 (ESPN).<br>
It should have rolled a single dice instead of two. The boardLocation occupation_name is not getting set.<br>
Status: **RESOLVED**</p>
Resolution: This Opportunity card has "choose_destination" as a pending_action.<br>
So there are two ways to play an occupation_choice Opportunity card:</p>
  a. specify the choice in the command line as in the above<br>
  b. resolve the choose_destination pending action in a second command</p>
The resolve method works correctly. I fixed (a) by issuing a "enter" instead of a "goto"

---
## Future Enhancements
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

---
## Technical TODOs
1. Make game_type ('points', 'timed') an Enum; add to GameConstants.<br>
Status: **COMPLETE**<br>
Implemented as GameType(Enum). This does not include "solo" as a type.<br>
That is indicated by CareersGame.solo: True if number of players == 1. The value is set when adding players</p>

2. CareersGameEngine.resolve(...) - change the `if what == PendingActionType` statements<br>
to use match() and case. This updated was made then reverted because eclipse was throwing
a null pointer exception. No idea why.<br>
Status: **OPEN**</p>

3. GameEngineCommands.execute_opportunity_card(...) - change the if(opportunity_type)...elif statements<br>
to match(opportunity_type): case OpportunityType.<whatever>.
Status: **OPEN**</p>


