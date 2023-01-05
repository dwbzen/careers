# Known Issues and Future Enhancements

---
## Known Issues
1. When resolving take_shortcut the player needs to roll or use an experience<br>
from the next_square. Currently it just goes to the next_square and executes it.<br>
Status: ACTIVE - "resolve take_shortcut yes" sets the player's board location to the space<br>
 BEFORE the next_square in the shortcut specialProcessing.<br>
 This works for UF but not for Pfizer because the square numbering is not consecutive.<br>
 When taking the shortcut the ordering is 1, 13, 14, 12, 15. <br>
 When not taking the shortcut the ordering is 1, 2, 3... 12, 15. </p>

2. The resolve select_degree command gets a syntax error on multi-word degree names:<br>
Business Admin, Computer Science. <br>
Change to single word: BusinessAdmin, ComputerScience OR concat the arguments into a single string.<br>
Status: COMPLETE. Change to parse_command_string to concatenate the resolve arguments
into a single string, for example:<br> `resolve("select_degree","Computer Science" )`</p>

3. If player 1 enters an Occupation and rolls (so they're on the Occupation path),
if player 2 lands on that occupation's entry square, the can_bump<br>
logic mistakenly adds player 1 to player 2's can_bump list.<br>
See `CareersGameEngine.who_occupies_my_square()` to fix.<br>
Status: OPEN</p>

4. The following commands should not be allowed when playing in solo production mode:
goto, advance, add degree, enter <occupation> when not on the target occupation entrance square<br>
Status: OPEN</p>

5. The perform command does not execute the perform string - the result
message is the JSON formatted command, but it's not executed.<br>
For example "perform roll 2" result message for player DWB is {"player": "DWB", "roll": 6, "dice": [3, 3]}<br>
The the "roll" isn't executed and so the player doesn't move.<br>
Also pending action(s) are not automatically resolved as described in the method comments.<br>
Status: OPEN</p>

6. Resolving select_degree with a missing or invalid degree program<br>
incorrectly clears the PendingActionType.SELECT_DEGREE pending action.<br>
Status: INVESTIGATING - problem is add_degree returns an error so the statement<br>
`if result.is_successful() and not player.on_holiday:`<br>
is False resulting in all pending actions being cleared.</p>

7. If a player lands on space 2 of Google (Pay $2000 OR go on Unemployment) and is unable to pay<br>
or elects not to pay, the player is sent to Unemployment but in passing Payday, collects<br>
their salary. This is wrong - the player should go directly to Unemployment and not go around the board to get there.<br>
Status: INVESTIGATING. This will also be a problem in Lister & Bacon, square 0.<br>
The CareersGameEngine._goto(...)  needs to look at the destination and if<br>
Unemployment, don't execute pass_payday </p>

8. If a player gets an error when resolving choose_occupation (by specifying College instead of <br>
an Occupation or specifying an Occupation that doesn't exist) the pending action<br>
is cleared incorrectly.<br>
Status: OPEN

---
## Future Enhancements
1. Currently entering an occupation requires 2 commands, for example:<br>
	`goto Amazon`<br>
	`enter Amazon`<br>
Expand the **enter** command to go to the occupation first (if not there already)<br>
**Note:** this should not be allowed when playing in solo production mode.<br>
Status: ACTIVE. Change completed, but still need to restrict in solo production game mode.</p>

2. If a player is currently on an occupation entry square, allow the **enter**
command without an argument to enter that occupation.<br>
For example if I'm on square 13 (Amazon occupation entry) I can issue
`enter` instead of `enter Amazon`<br>
If the player is not on an Occupation entry square, return an error.<br>
Status: OPEN</p>

3. Implement a timed game type (i.e. a game that lasts a set number of minutes).<br>
It can be specified in GameRunner with **--type timed** command line argument,<br>
but the implementation is missing. Timer should start when the **start** command is executed,<br>
and checked at the end of each players turn (on the next command).

---
## Technical TODOs
1. Make game_type ('points', 'timed', 'solo') an Enum; add to GameConstants.<br>
Status: OPEN</p>

2. CareersGameEngine.resolve(...) - change the `if what == PendingActionType` statements<br>
to use match() and case. This updated was made then reverted because eclipse was throwing
a null pointer exception. No idea why.<br>
Status: OPEN</p>

3. GameEngineCommands.execute_opportunity_card(...) - change the if(opportunity_type)...elif statements<br>
to match(opportunity_type): case OpportunityType.<whatever>.
Status: OPEN</p>


