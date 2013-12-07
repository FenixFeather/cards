cards to cards
=====

Engine for concept-to-description/category matching game.

How to use: Linux/Unix
----------
- Run cards_server.py
- Each client should run "cards_client.py" or "cards_gui_client.py" and connect to the server.
- Play!

How to use: Windows
----------
- You can use the installer to install the program.
- Run cards_server.exe if there is no server
- Each client should then run either "cards_client.exe" or "cards_gui_client.exe" and connect to the server

Configuring Cards
-----------
- Simply change the settings in settings.ini to point to the correct text files.
- Decks should consist of text files with each card separated by a new line.
- Cards uses port 2809 by default. You can change this in the settings.ini

Notes on Drop-in-Drop-out
-----------
- Players can drop in whenever they want. They will be able to play once the current round finishes.
- If a player leaves the game, and their card is chosen as the winner, nobody will win.
- If a player leaves a game before their turn to submit a card, the game proceeds normally.
- If a player who will be judging leaves the game, then the server will randomly choose a winner.

Note on Cards Against Humanity Deck
-----------
- The Cards Against Humanity decks are the intellectual property of Cards Against Humanity LLC.
- It is distributed under a Creative Commons BY-NC-SA 2.0 license. The license is viewable here.
- Their website is available at http://cardsagainsthumanity.com
- The black deck is the descriptors, and the white deck is the entities.
- This app isn't endorsed by or affiliated with Cards Against Humanity LLC.
