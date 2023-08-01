
# Developer Guide

## Python Project

### Commands

Here is a complete list of valid GameEngine commands:

'add', 'add_degree', 'advance', 'bankrupt', 'bump', 'buy', <br>
'create', 'done', 'end', 'enter', '_enter', 'game_status', 'goto',<br>
'help', 'info', 'list', 'load', 'location', 'log_message', 'lose_turn',<br>
'need', 'next', 'pay', 'perform', 'quit', 'retire', 'roll', 'resolve',<br>
 'save', 'saved', 'set', 'start', 'status', 'take_turn', 'transfer', 'turn_history',<br>
'update', 'use', 'use_insurance', 'where', 'who'</p>

## InDesign Model
The game board layout is maintained with Adobe InDesign. This section documents the conventions and metadata used in the model. The metadata drives the board appearance in the Unity UI.

For the purposes of this document "occupation square" refers to the individual squares in an occupation, profession, or destination.

### Board Layout
The layout consists of 42 border squares and 128 occupation squares. <br>Border squares are arranged in a 10 square by 13 array around the edges of the board.<br>
Border squares are numbered starting with Payday as square 0.<br> 
There are 6 types of border squares:

* Corner Squares: Payday, Hospital, Unemployment and
 Vacation. They are also referred to as “destination squares.”

* Action Squares: Six action squares are highlighted in light blue.

* Danger Squares are highlighted in light red. Landing on a danger<br> square results in the loss of cash-on-hand.

* Transportation Squares - depending on the Edition, there are the four alternating<br>transportation squares: bus, rail, or air.

* Occupation Entrance Squares have a tan background and also an arrow<br>indicating the entrance direction

All game squares have metadata consisting of a tag, and optionally an XML attribute and export option.

### Tags
Tags can be viewed in InDesign by selecting Windows -> Utilities -> Tags in the main menu. Tags form the basis for Structure. To view the structure select View -> Structure -> Show Structure in the main menu.

All rectangles, and some images, are tagged as follows:<br>
* border - applies to all border squares
* heart - each individual heart image is tagged with heart
* star - each individual star image is tagged with star
* occupation - applies to each occupation square except in college
* college - applies to each college occupation square
* common - applies to the green rectangles and text frames in the college area
* arrow - applies to the arrow graphic in each occupation entrance square
* board_center - applied to the layer 2 background images and rectangle

### XML Atributes
XML attributes are assigned and viewed in the InDesign Structure pane.<br>
Here is a list of XML attributes by Structure Tag:

* occupation, college:
    * type = occupation_square
    * occupation = the occupation alternate name. These are given by the "gameboard_mapping" element of occupations.json.

* border: type refers to the type of border square and is one of:
    * occupation_entrance_square
    * opportunity_square
    * danger_square
    * travel_square
    * corner_square
    * action_square

### Export Options
Export options are viewed and assigned by right clicking on the game square rectangle and selecting "Object Export Options..." from the pop-up menu. Values are assigned as "Alt Text", with a Custom alt text source.

**Every** game square is assigned an ordinal number. Border squares are numbered from 0 to 41. The number is the "number" element in the gameLayout JSON file.

Occupation squares are numbered from 0 to #squares-1. The number is the "number" element in the occupation JSON file.


