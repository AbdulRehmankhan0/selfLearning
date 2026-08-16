3# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 22:42:36 2026

@author: user
"""

import random  # Imports random for Easy and Medium AI moves.
import heapq  # Imports heapq for priority-based move ordering.
import json  # Imports json for saving and loading AI memory.
import os  # Imports os for checking whether the memory file exists.


MEMORY_FILE = "tic_tac_toe_memory.json"  # Stores the AI memory filename.

WINNING_LINES_CACHE = {}  # Stores winning lines so they are calculated only once.

TRANSPOSITION_TABLE = {}  # Stores previously calculated Minimax positions.

EXACT_SCORE = 0  # Marks a cached score as the true Minimax value.
LOWER_BOUND = 1  # Marks a cached score as only a lower bound (from a beta cutoff).
UPPER_BOUND = 2  # Marks a cached score as only an upper bound (from an alpha cutoff).


# ============================================================
# MEMORY SYSTEM
# ============================================================

def create_default_memory():  # Creates a fresh memory structure.
    return {  # Returns the default memory dictionary.
        "total_games": 0,  # Stores total games played.
        "player_wins": 0,  # Stores player victories.
        "ai_wins": 0,  # Stores AI victories.
        "draws": 0,  # Stores draws.

        "difficulty_games": {  # Stores games played at each difficulty.
            "easy": 0,  # Stores Easy games.
            "medium": 0,  # Stores Medium games.
            "hard": 0,  # Stores Hard games.
            "extreme": 0,  # Stores Extreme games.
        },

        "board_games": {  # Stores games played on each board size.
            "3x3": 0,  # Stores 3x3 games.
            "4x4": 0,  # Stores 4x4 games.
            "5x5": 0,  # Stores 5x5 games.
        },

        "history": []  # Stores previous game records.
    }


def load_memory():  # Loads saved AI memory.
    default_memory = create_default_memory()  # Creates default memory.

    if not os.path.exists(MEMORY_FILE):  # Checks whether the memory file exists.
        return default_memory  # Returns fresh memory if no file exists.

    try:  # Starts error handling.
        with open(MEMORY_FILE, "r") as file:  # Opens the memory file.
            memory = json.load(file)  # Converts JSON into Python data.

        if not isinstance(memory, dict):  # Checks whether memory has correct format.
            return default_memory  # Returns fresh memory if format is invalid.

        for key, value in default_memory.items():  # Checks all required sections.
            if key not in memory:  # Checks for missing sections.
                memory[key] = value  # Restores missing sections.

        for difficulty in default_memory["difficulty_games"]:  # Checks difficulties.
            if difficulty not in memory["difficulty_games"]:  # Checks missing difficulty.
                memory["difficulty_games"][difficulty] = 0  # Adds missing difficulty.

        for board_name in default_memory["board_games"]:  # Checks board sizes.
            if board_name not in memory["board_games"]:  # Checks missing board size.
                memory["board_games"][board_name] = 0  # Adds missing board size.

        if not isinstance(memory["history"], list):  # Checks history format.
            memory["history"] = []  # Resets invalid history.

        return memory  # Returns loaded memory.

    except (OSError, json.JSONDecodeError, TypeError):  # Handles memory errors.
        print("⚠️ AI memory could not be loaded. Starting fresh memory.")  # Shows warning.
        return default_memory  # Returns new memory.


def save_memory(memory):  # Saves AI memory.
    try:  # Starts error handling.
        with open(MEMORY_FILE, "w") as file:  # Opens memory file for writing.
            json.dump(memory, file, indent=4)  # Saves formatted JSON.

    except OSError:  # Handles file-writing errors.
        print("⚠️ AI memory could not be saved.")  # Shows warning.


def remember_game(memory, result, difficulty, size):  # Saves completed game information.
    memory["total_games"] += 1  # Increases total games.

    if result == "X":  # Checks whether player won.
        memory["player_wins"] += 1  # Increases player wins.
        result_name = "Player won"  # Stores readable result.

    elif result == "O":  # Checks whether AI won.
        memory["ai_wins"] += 1  # Increases AI wins.
        result_name = "AI won"  # Stores readable result.

    else:  # Runs when the game was a draw.
        memory["draws"] += 1  # Increases draw count.
        result_name = "Draw"  # Stores readable result.

    memory["difficulty_games"][difficulty] += 1  # Records difficulty.

    board_name = f"{size}x{size}"  # Creates board-size name.
    memory["board_games"][board_name] += 1  # Records board size.

    memory["history"].append({  # Adds a new game record.
        "game_number": memory["total_games"],  # Stores game number.
        "result": result_name,  # Stores game result.
        "difficulty": difficulty,  # Stores difficulty.
        "board_size": board_name  # Stores board size.
    })

    if len(memory["history"]) > 100:  # Checks whether history is too large.
        memory["history"] = memory["history"][-100:]  # Keeps the newest 100 games.

    save_memory(memory)  # Saves updated memory.


def show_memory(memory):  # Displays AI memory.
    print("\n================ AI MEMORY ================")  # Displays heading.

    print("Total games:", memory["total_games"])  # Displays total games.
    print("Player wins:", memory["player_wins"])  # Displays player wins.
    print("AI wins:", memory["ai_wins"])  # Displays AI wins.
    print("Draws:", memory["draws"])  # Displays draws.

    print("\nGames by difficulty:")  # Displays difficulty heading.
    print("Easy:", memory["difficulty_games"]["easy"])  # Displays Easy games.
    print("Medium:", memory["difficulty_games"]["medium"])  # Displays Medium games.
    print("Hard:", memory["difficulty_games"]["hard"])  # Displays Hard games.
    print("Extreme:", memory["difficulty_games"]["extreme"])  # Displays Extreme games.

    print("\nGames by board size:")  # Displays board-size heading.
    print("3x3:", memory["board_games"]["3x3"])  # Displays 3x3 games.
    print("4x4:", memory["board_games"]["4x4"])  # Displays 4x4 games.
    print("5x5:", memory["board_games"]["5x5"])  # Displays 5x5 games.

    if memory["history"]:  # Checks whether game history exists.
        print("\nRecent games:")  # Displays history heading.

        for game in memory["history"][-10:]:  # Shows latest ten games.
            print(
                f"Game {game['game_number']} - "
                f"{game['result']} - "
                f"{game['difficulty']} - "
                f"{game['board_size']}"
            )  # Displays game record.

    else:  # Runs when no history exists.
        print("\nNo previous games are stored yet.")  # Displays empty message.

    print("===========================================\n")  # Ends memory section.


# ============================================================
# BOARD SYSTEM
# ============================================================

def choose_board_size():  # Allows the player to choose the board size.
    while True:  # Keeps asking until valid input is received.
        print("\nChoose your board size:")  # Displays board menu.
        print("1. 3x3 - Classic Tic-Tac-Toe")  # Displays 3x3.
        print("2. 4x4 - Four in a row")  # Displays 4x4.
        print("3. 5x5 - Five in a row")  # Displays 5x5.

        choice = input("Enter 1, 2, or 3: ").strip().lower()  # Gets choice.

        if choice in ("1", "3x3"):  # Checks 3x3.
            return 3  # Returns board size 3.

        if choice in ("2", "4x4"):  # Checks 4x4.
            return 4  # Returns board size 4.

        if choice in ("3", "5x5"):  # Checks 5x5.
            return 5  # Returns board size 5.

        print("❌ Invalid choice. Please enter 1, 2, or 3.")  # Shows error.


def choose_difficulty():  # Allows the player to choose the AI difficulty.
    while True:  # Keeps asking until valid input is received.
        print("\nChoose AI difficulty:")  # Displays difficulty menu.
        print("1. Easy - Random moves")  # Displays Easy.
        print("2. Medium - Sometimes makes mistakes")  # Displays Medium.
        print("3. Hard - Optimized Minimax")  # Displays Hard.
        print("4. Extreme - Deep Alpha-Beta search")  # Displays Extreme.

        choice = input("Enter 1, 2, 3, or 4: ").strip().lower()  # Gets choice.

        if choice in ("1", "easy"):  # Checks Easy.
            return "easy"  # Returns Easy difficulty.

        if choice in ("2", "medium"):  # Checks Medium.
            return "medium"  # Returns Medium difficulty.

        if choice in ("3", "hard"):  # Checks Hard.
            return "hard"  # Returns Hard difficulty.

        if choice in ("4", "extreme"):  # Checks Extreme.
            return "extreme"  # Returns Extreme difficulty.

        print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")  # Shows error.


def get_winning_lines(size):  # Creates all winning lines for a board size.
    if size in WINNING_LINES_CACHE:  # Checks whether lines already exist.
        return WINNING_LINES_CACHE[size]  # Returns cached lines.

    lines = []  # Creates winning-line list.

    for row in range(size):  # Goes through every row.
        lines.append(
            tuple(row * size + column for column in range(size))
        )  # Adds row.

    for column in range(size):  # Goes through every column.
        lines.append(
            tuple(row * size + column for row in range(size))
        )  # Adds column.

    lines.append(
        tuple(i * size + i for i in range(size))
    )  # Adds main diagonal.

    lines.append(
        tuple(i * size + (size - 1 - i) for i in range(size))
    )  # Adds opposite diagonal.

    WINNING_LINES_CACHE[size] = lines  # Saves lines for future use.

    return lines  # Returns winning lines.


def show_board(board, size):  # Displays the selected board.
    print()  # Adds spacing.

    for row in range(size):  # Goes through rows.
        values = []  # Creates row values.

        for column in range(size):  # Goes through columns.
            position = row * size + column  # Calculates position.
            values.append(board[position])  # Adds symbol.

        print(" | ".join(values))  # Displays row.

        if row < size - 1:  # Checks whether another row exists.
            print("---+" * (size - 1) + "---")  # Displays separator.

    print()  # Adds spacing.


def check_winner(board, size):  # Checks the current game result.
    for line in get_winning_lines(size):  # Checks every winning line.
        first = board[line[0]]  # Gets first symbol.

        if first != " " and all(board[position] == first for position in line):
            return first  # Returns the winner.

    if " " not in board:  # Checks whether board is full.
        return "Draw"  # Returns draw.

    return None  # Returns None while game continues.


def get_empty_spaces(board):  # Gets empty positions.
    return [i for i, value in enumerate(board) if value == " "]  # Returns indexes.


# ============================================================
# AI EVALUATION
# ============================================================

def evaluate_board(board, size):  # Evaluates a non-terminal board.
    score = 0  # Starts evaluation score.

    for line in get_winning_lines(size):  # Checks every winning line.
        ai_count = 0  # Counts O symbols.
        player_count = 0  # Counts X symbols.

        for position in line:  # Checks every position.
            if board[position] == "O":  # Checks AI symbol.
                ai_count += 1  # Increases AI count.

            elif board[position] == "X":  # Checks player symbol.
                player_count += 1  # Increases player count.

        if player_count == 0 and ai_count > 0:  # Checks AI-only line.
            score += 2 ** ai_count  # Rewards AI potential.

        elif ai_count == 0 and player_count > 0:  # Checks player-only line.
            score -= 2 ** player_count  # Punishes player potential.

    return score  # Returns evaluation score.


def find_immediate_move(board, size, symbol):  # Finds an immediate winning move.
    for position in get_empty_spaces(board):  # Checks empty spaces.
        board[position] = symbol  # Temporarily places symbol.

        if check_winner(board, size) == symbol:  # Checks whether it wins.
            board[position] = " "  # Restores empty space.
            return position  # Returns winning move.

        board[position] = " "  # Restores empty space.

    return None  # No immediate winning move exists.


def ordered_moves(board, size, maximizing):  # Orders moves for faster Alpha-Beta.
    empty_spaces = get_empty_spaces(board)  # Gets available moves.

    if not empty_spaces:  # Checks whether no moves exist.
        return []  # Returns empty list.

    symbol = "O" if maximizing else "X"  # Chooses current symbol.

    opponent = "X" if maximizing else "O"  # Chooses opponent symbol.

    winning_move = find_immediate_move(board, size, symbol)  # Searches for winning move.

    blocking_move = find_immediate_move(board, size, opponent)  # Searches for block.

    if winning_move is not None:  # Checks for immediate victory.
        return [winning_move] + [
            move for move in empty_spaces if move != winning_move
        ]  # Searches winning move first.

    if blocking_move is not None:  # Checks whether blocking is necessary.
        return [blocking_move] + [
            move for move in empty_spaces if move != blocking_move
        ]  # Searches blocking move first.

    center = size // 2  # Finds center coordinate.

    moves = []  # Creates priority queue.

    for position in empty_spaces:  # Checks every available move.
        row = position // size  # Calculates row.
        column = position % size  # Calculates column.

        distance = abs(row - center) + abs(column - center)  # Calculates center distance.

        priority = (size * 2 - distance) * 2  # Gives central moves higher priority.

        if row in (0, size - 1) and column in (0, size - 1):  # Checks corners.
            priority += 10  # Gives corners extra priority.

        heapq.heappush(moves, (-priority, position))  # Adds move to queue.

    result = []  # Creates ordered move list.

    while moves:  # Continues until queue is empty.
        _, position = heapq.heappop(moves)  # Gets highest-priority move.
        result.append(position)  # Adds move.

    return result  # Returns ordered moves.


# ============================================================
# SEARCH DEPTH
# ============================================================

def get_search_depth(size, difficulty):  # Selects AI search depth.
    if size == 3:  # Checks 3x3.
        return None  # Searches complete game tree.

    if size == 4:  # Checks 4x4.
        if difficulty == "extreme":  # Checks Extreme.
            return 6  # Searches six levels deep.

        return 4  # Hard uses four levels.

    if difficulty == "extreme":  # Checks Extreme 5x5.
        return 5  # Searches five levels.

    return 3  # Hard uses three levels.


# ============================================================
# OPTIMIZED MINIMAX
# ============================================================

def minimax(
    board,
    size,
    maximizing,
    alpha,
    beta,
    depth,
    max_depth
):  # Defines optimized Minimax with Alpha-Beta pruning.

    result = check_winner(board, size)  # Checks terminal result.

    if result == "O":  # Checks AI victory.
        return 100000 - depth  # Rewards faster AI victory.

    if result == "X":  # Checks player victory.
        return -100000 + depth  # Punishes AI loss.

    if result == "Draw":  # Checks draw.
        return 0  # Draw is neutral.

    if max_depth is not None and depth >= max_depth:  # Checks depth limit.
        return evaluate_board(board, size)  # Uses heuristic evaluation.

    original_alpha = alpha  # Remembers the incoming Alpha for bound classification.
    original_beta = beta  # Remembers the incoming Beta for bound classification.

    state = (
        tuple(board),
        size,
        maximizing,
        depth,
        max_depth
    )  # Creates a unique cache key.

    if state in TRANSPOSITION_TABLE:  # Checks cached position.
        cached_score, flag = TRANSPOSITION_TABLE[state]  # Reads cached score and its bound type.

        if flag == EXACT_SCORE:  # Checks whether the cached value is exact.
            return cached_score  # Safe to reuse directly.

        if flag == LOWER_BOUND:  # Checks whether the cached value is only a lower bound.
            alpha = max(alpha, cached_score)  # Tightens Alpha using the bound.

        elif flag == UPPER_BOUND:  # Checks whether the cached value is only an upper bound.
            beta = min(beta, cached_score)  # Tightens Beta using the bound.

        if alpha >= beta:  # Checks whether the tightened window already cuts off.
            return cached_score  # Safe to reuse as a cutoff value.
        # Otherwise the cached bound isn't tight enough here, so fall through
        # and recompute this position under the current Alpha-Beta window.

    if maximizing:  # Checks whether it is AI's turn.
        best_score = -float("inf")  # Starts with lowest score.

        for position in ordered_moves(board, size, True):  # Searches best moves first.
            board[position] = "O"  # Places AI symbol.

            score = minimax(
                board,
                size,
                False,
                alpha,
                beta,
                depth + 1,
                max_depth
            )  # Searches future position.

            board[position] = " "  # Undoes move.

            best_score = max(best_score, score)  # Keeps best AI score.

            alpha = max(alpha, best_score)  # Updates Alpha.

            if alpha >= beta:  # Checks Alpha-Beta cutoff.
                break  # Stops unnecessary search.

    else:  # Runs when it is player's turn.
        best_score = float("inf")  # Starts with highest score.

        for position in ordered_moves(board, size, False):  # Searches best player moves first.
            board[position] = "X"  # Places player symbol.

            score = minimax(
                board,
                size,
                True,
                alpha,
                beta,
                depth + 1,
                max_depth
            )  # Searches future position.

            board[position] = " "  # Undoes move.

            best_score = min(best_score, score)  # Keeps lowest score.

            beta = min(beta, best_score)  # Updates Beta.

            if alpha >= beta:  # Checks Alpha-Beta cutoff.
                break  # Stops unnecessary search.

    if best_score <= original_alpha:  # Checks whether the search failed low.
        flag = UPPER_BOUND  # True value is at most best_score.

    elif best_score >= original_beta:  # Checks whether the search failed high.
        flag = LOWER_BOUND  # True value is at least best_score.

    else:  # Runs when the search completed within the window.
        flag = EXACT_SCORE  # True value was fully determined.

    TRANSPOSITION_TABLE[state] = (best_score, flag)  # Saves score with its bound type.

    return best_score  # Returns best score.


# ============================================================
# AI MOVE FUNCTIONS
# ============================================================

def find_best_move(board, size, difficulty):  # Finds the best move.
    empty_spaces = get_empty_spaces(board)  # Gets empty spaces.

    if not empty_spaces:  # Checks whether no moves exist.
        return None  # Returns no move.

    # Checks immediate victory before expensive Minimax.
    winning_move = find_immediate_move(board, size, "O")  # Searches AI winning move.

    if winning_move is not None:  # Checks whether a winning move exists.
        return winning_move  # Immediately takes the winning move.

    # Checks whether AI must block the player.
    blocking_move = find_immediate_move(board, size, "X")  # Searches player threat.

    if blocking_move is not None:  # Checks whether blocking is required.
        return blocking_move  # Immediately blocks player.

    TRANSPOSITION_TABLE.clear()  # Clears previous decision cache.

    max_depth = get_search_depth(size, difficulty)  # Gets appropriate depth.

    best_score = -float("inf")  # Starts with lowest score.

    best_move = empty_spaces[0]  # Provides safe fallback.

    for position in ordered_moves(board, size, True):  # Searches promising moves first.
        board[position] = "O"  # Temporarily places O.

        score = minimax(
            board,
            size,
            False,
            -float("inf"),
            float("inf"),
            1,
            max_depth
        )  # Calculates future score.

        board[position] = " "  # Removes temporary O.

        if score > best_score:  # Checks whether this move is better.
            best_score = score  # Saves best score.
            best_move = position  # Saves best move.

    return best_move  # Returns strongest move.


def easy_move(board, size):  # Creates an Easy AI move.
    empty_spaces = get_empty_spaces(board)  # Gets empty spaces.

    if not empty_spaces:  # Checks whether no spaces remain.
        return None  # Returns no move.

    return random.choice(empty_spaces)  # Makes random move.


def medium_move(board, size):  # Creates Medium AI move.
    empty_spaces = get_empty_spaces(board)  # Gets empty spaces.

    if not empty_spaces:  # Checks whether no spaces remain.
        return None  # Returns no move.

    if random.random() < 0.40:  # Gives Medium a 40 percent mistake chance.
        return random.choice(empty_spaces)  # Makes random move.

    return find_best_move(board, size, "medium")  # Uses optimized search.


def extreme_move(board, size):  # Creates the strongest AI move.
    empty_spaces = get_empty_spaces(board)  # Gets available positions.

    if not empty_spaces:  # Checks whether board is full.
        return None  # Returns no move.

    # Extreme AI immediately takes a winning opportunity.
    winning_move = find_immediate_move(board, size, "O")  # Searches winning move.

    if winning_move is not None:  # Checks for winning move.
        return winning_move  # Takes it immediately.

    # Extreme AI immediately blocks an opponent win.
    blocking_move = find_immediate_move(board, size, "X")  # Searches threat.

    if blocking_move is not None:  # Checks for threat.
        return blocking_move  # Blocks immediately.

    TRANSPOSITION_TABLE.clear()  # Clears old calculations.

    max_depth = get_search_depth(size, "extreme")  # Gets deeper Extreme depth.

    best_score = -float("inf")  # Starts with lowest score.

    best_move = empty_spaces[0]  # Provides fallback move.

    for position in ordered_moves(board, size, True):  # Searches promising moves first.
        board[position] = "O"  # Temporarily places O.

        score = minimax(
            board,
            size,
            False,
            -float("inf"),
            float("inf"),
            1,
            max_depth
        )  # Performs deep Alpha-Beta Minimax.

        board[position] = " "  # Removes temporary move.

        if score > best_score:  # Checks whether score is better.
            best_score = score  # Saves score.
            best_move = position  # Saves move.

    return best_move  # Returns strongest move.


def choose_ai_move(board, difficulty, size):  # Selects the AI strategy.
    if difficulty == "easy":  # Checks Easy.
        return easy_move(board, size)  # Uses random AI.

    if difficulty == "medium":  # Checks Medium.
        return medium_move(board, size)  # Uses partly intelligent AI.

    if difficulty == "hard":  # Checks Hard.
        return find_best_move(board, size, "hard")  # Uses optimized Minimax.

    if difficulty == "extreme":  # Checks Extreme.
        return extreme_move(board, size)  # Uses deep optimized Minimax.

    return find_best_move(board, size, "hard")  # Safety fallback.


# ============================================================
# SMART PREDICTION
# ============================================================

def predict_result(board, size, next_player):  # Predicts only useful outcomes.
    result = check_winner(board, size)  # Checks current result.

    if result == "O":  # Checks AI victory.
        return "AI has already won!"  # Reports AI win.

    if result == "X":  # Checks player victory.
        return "You have already won!"  # Reports player win.

    if result == "Draw":  # Checks draw.
        return "The game is already a tie!"  # Reports draw.

    empty_count = len(get_empty_spaces(board))  # Counts remaining moves.

    # Avoids unnecessary expensive predictions early in larger games.
    if size == 5 and empty_count > 10:  # Checks early 5x5 game.
        return None  # No prediction yet.

    if size == 4 and empty_count > 7:  # Checks early 4x4 game.
        return None  # No prediction yet.

    TRANSPOSITION_TABLE.clear()  # Clears old search cache.

    # Uses full search on 3x3.
    if size == 3:  # Checks 3x3.
        max_depth = None  # Searches complete game tree.

    else:  # Runs for larger boards.
        max_depth = 3  # Uses limited prediction search.

    maximizing = next_player == "O"  # Determines current player.

    score = minimax(
        board,
        size,
        maximizing,
        -float("inf"),
        float("inf"),
        0,
        max_depth
    )  # Calculates prediction score.

    if size == 3:  # Gives exact 3x3 prediction.
        if score > 0:  # Checks AI winning path.
            return "niazi predicts that AI can force a win."

        if score < 0:  # Checks player winning path.
            return "niazi predicts that you can force a win."

        return "With perfect play, this game can end in a tie."

    if score >= 100000:  # Checks forced AI victory.
        return "AI has found a winning path!"

    if score <= -100000:  # Checks forced player victory.
        return "You have a winning path!"

    return None  # Does not announce uncertain results.


# ============================================================
# GAME LOOP
# ============================================================

def play_game(memory):  # Runs one complete game.
    size = choose_board_size()  # Gets board size.

    difficulty = choose_difficulty()  # Gets AI difficulty.

    board = [" "] * (size * size)  # Creates correct board size.

    print("\n=================================")  # Displays border.
    print("       AI TIC-TAC-TOE GAME")  # Displays title.
    print("=================================")  # Displays border.

    print("\nYou are X.")  # Explains player symbol.
    print("AI is O.")  # Explains AI symbol.
    print(f"Board size: {size}x{size}")  # Displays board size.
    print(f"Difficulty: {difficulty.capitalize()}")  # Displays difficulty.

    print("\nPosition numbers:")  # Displays position instructions.

    for row in range(size):  # Goes through rows.
        numbers = []  # Creates row numbers.

        for column in range(size):  # Goes through columns.
            numbers.append(str(row * size + column + 1))  # Adds position number.

        print(" | ".join(numbers))  # Displays row.

        if row < size - 1:  # Checks whether another row exists.
            print("---+" * (size - 1) + "---")  # Displays separator.

    while True:  # Main game loop.
        show_board(board, size)  # Displays current board.

        try:  # Starts input handling.
            choice = int(input("Enter your position: "))  # Gets player move.

        except ValueError:  # Handles non-number input.
            print("❌ Please enter a valid number.")  # Shows error.
            continue  # Asks again.

        position = choice - 1  # Converts position to index.

        if position < 0 or position >= len(board):  # Checks valid range.
            print(
                f"❌ Choose a number from 1 to {len(board)}."
            )  # Shows valid range.
            continue  # Asks again.

        if board[position] != " ":  # Checks whether position is occupied.
            print("❌ That position is already taken.")  # Shows error.
            continue  # Asks again.

        board[position] = "X"  # Places player's X.

        result = check_winner(board, size)  # Checks player result.

        if result is not None:  # Checks whether game ended.
            show_board(board, size)  # Displays final board.

            if result == "X":  # Checks player win.
                print("🎉 Congratulations! You won!")

            else:  # Handles draw.
                print("🤝 The game ended in a tie!")

            remember_game(
                memory,
                result,
                difficulty,
                size
            )  # Saves game.

            return  # Ends game.

        prediction = predict_result(
            board,
            size,
            "O"
        )  # Gets useful prediction.

        if prediction is not None:  # Checks whether prediction exists.
            print("\n🧠 AI prediction:", prediction)  # Displays prediction.

        if difficulty == "extreme":  # Checks Extreme mode.
            print("\n☠️ EXTREME AI is calculating deeply...")  # Shows Extreme message.
            print("Alpha-Beta pruning is active.")  # Explains optimization.

        elif difficulty == "hard":  # Checks Hard mode.
            print("\n🤖 AI is calculating the best move...")  # Shows Hard message.

        else:  # Handles Easy and Medium.
            print("\n🧠 AI is thinking...")  # Shows normal message.

        ai_position = choose_ai_move(
            board,
            difficulty,
            size
        )  # Calculates AI move.

        if ai_position is None:  # Safety check.
            print("No moves are available.")  # Shows safety message.
            return  # Ends game.

        board[ai_position] = "O"  # Places AI O.

        print(
            f"\nAI played position {ai_position + 1}."
        )  # Shows AI position.

        result = check_winner(board, size)  # Checks AI result.

        if result is not None:  # Checks whether game ended.
            show_board(board, size)  # Displays final board.

            if result == "O":  # Checks AI victory.
                print("🤖 AI wins! Better luck next time!")

            else:  # Handles draw.
                print("🤝 The game ended in a tie!")

            remember_game(
                memory,
                result,
                difficulty,
                size
            )  # Saves game.

            return  # Ends game.

        prediction = predict_result(
            board,
            size,
            "X"
        )  # Predicts next result.

        if prediction is not None:  # Checks prediction.
            print("\n🧠 AI prediction:", prediction)  # Displays prediction.


def play_again():  # Asks whether player wants another game.
    while True:  # Keeps asking until valid input.
        answer = input(
            "\nDo you want to play again? (yes/no): "
        ).strip().lower()  # Gets answer.

        if answer in ("yes", "y"):  # Checks yes.
            return True  # Starts another game.

        if answer in ("no", "n"):  # Checks no.
            return False  # Stops program.

        print("Please type yes or no.")  # Shows error.


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():  # Defines main program.
    memory = load_memory()  # Loads AI memory.

    print("\n🎮 Welcome to AI Tic-Tac-Toe!")  # Displays welcome.

    if memory["total_games"] > 0:  # Checks previous games.
        print("🧠 I remember your previous games!")  # Shows memory message.
        print(
            "Previous games remembered:",
            memory["total_games"]
        )  # Displays count.

        show_memory(memory)  # Displays memory.

    else:  # Runs for a new player.
        print(
            "🧠 This is my first game, so my memory is empty."
        )  # Shows first-game message.

    while True:  # Allows multiple games.
        play_game(memory)  # Starts one game.

        print("\n🧠 Game saved to AI memory!")  # Confirms save.

        show_memory(memory)  # Displays updated memory.

        if play_again():  # Asks whether to continue.
            print("\n🔥 Starting a new game!")  # Announces next game.

        else:  # Runs when player stops.
            print("\nThanks for playing! 👋")  # Says goodbye.
            print("See you next time!")  # Final message.
            break  # Ends program.


if __name__ == "__main__":  # Checks whether file is being run directly.
    main()  # Starts the game.