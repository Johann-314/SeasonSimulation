"""
Purpose: Enter additional result by hand, without having to Code it directly into Python
Largely vibe-coded module, made mostly redundant by SaveData and Excel 
"""

import tkinter as tk
import copy

#only first experiments - mostly self-coded

def enterResults(games,gamesFT=[25,25,15],force=False):
    newgames=copy.deepcopy(games)
    
    for g in newgames:
        if not g[1]:
            for i in range(len(gamesFT)):
                final=gamesFT[i]
                def data_entry():
                    def submit():
                        s1=score1.get()
                        s2=score2.get()
                        valid=False
                        if s1>=i:
                            if (s1==i and 0<=s2<=i-2) or (s1>i and s2==s1-2):
                                valid=True
                        elif s2>=i:
                            if (s2==i and 0<=s1<=i-2) or (s2>i and s1==s2-2):
                                valid=True
                        else:
                            valid=False
                        if valid:
                            g[1].append([score1.get(),score2.get()])
                            root.destroy()
                        else:
                            root.destroy()
                            data_entry()
                    root = tk.Tk()
                    root.geometry("800x600")
                    root.title(g[0][0] + "vs" + g[0][1] + ", Game " + str(i+1)) 
                    score1=tk.IntVar()
                    score2=tk.IntVar()
                    tk.Label(root, text=g[0][0]).pack(padx=20,pady=20)
                    tk.Entry(root, textvariable=score1).pack()

                    tk.Label(root, text=g[0][1]).pack(padx=20,pady=20)
                    tk.Entry(root, textvariable=score2).pack()

                    tk.Button(root, text="Submit", command=submit).pack()
                    
                    root.mainloop()
                data_entry()
    return newgames

#print(enterResults([[["A","B"],[]]],gamesFT=[25]))

############################################################
#vibe-coded:

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Tuple

default_callback = lambda x:None

class MatchResultsEntry:
    """A tkinter widget for entering results for unplayed matches with set-based scoring."""
    
    def __init__(self, parent: tk.Widget, games: List, 
                 on_submit: Callable[[List], None] = default_callback,
                 show_played: bool = False,
                 set_formats: List[int] = [25,25,15]):
        """
        Initialize the match results entry form.
        
        Args:
            games: List of games in format [["Team A", "Team B"], [[], [], ...]] or similar
                   - games[i][0] = [home_team, away_team]
                   - games[i][1] = list of score sets ([] means unplayed, [score_set] means played)
            on_submit: Callback function that receives the updated games list
            show_played: Whether to display already-played games (default: False)
            set_formats: List of "first to" values for each set, e.g. [11, 11, 11] for best-of-3 to 11
                        Two-lead rule is automatically applied. If None, no validation is performed.
        """
        self.parent = parent
        self.games = games
        if on_submit is default_callback:
            def _set_as_games(results):
                self.results=results
            self.on_submit=_set_as_games
        else:
            self.on_submit=on_submit
        self.show_played = show_played
        self.set_formats = set_formats or []
        self.game_entries = []
        self.results = []
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_widgets()
    
    def _is_valid_score(self, home_score: int, away_score: int, set_num: int) -> Tuple[bool, str]:
        """
        Validate a score for a given set.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.set_formats or set_num >= len(self.set_formats):
            return True, ""
        
        first_to = self.set_formats[set_num]
        
        # Both scores must be non-negative
        if home_score < 0 or away_score < 0:
            return False, f"Scores cannot be negative"
        
        # Check if set is over (one team has reached first_to with 2-lead)
        home_wins = home_score >= first_to and (home_score - away_score) >= 2
        away_wins = away_score >= first_to and (away_score - home_score) >= 2
        
        if not (home_wins or away_wins):
            # Set is not finished yet - scores must be reasonable
            if home_score >= first_to + 2 or away_score >= first_to + 2:
                return False, f"Invalid: Set should be over at this score (first to {first_to})"
            return True, ""
        
        if home_wins and away_wins:
            return False, f"Both teams cannot win (first to {first_to})"
        
        return True, ""
    
    def _is_match_over(self, score_sets: List) -> Tuple[bool, str]:
        """
        Check if a match is already decided based on score sets.
        
        Returns:
            Tuple of (is_match_over, reason)
        """
        if not self.set_formats or len(self.set_formats) == 0:
            return False, ""
        
        # Determine sets needed to win
        sets_needed = (len(self.set_formats) // 2) + 1
        
        home_sets_won = 0
        away_sets_won = 0
        
        for set_idx, score_set in enumerate(score_sets):
            if set_idx >= len(self.set_formats):
                return False, "Too many sets played"
            
            first_to = self.set_formats[set_idx]
            home_score, away_score = score_set
            
            # Check if this set is valid
            home_wins_set = home_score >= first_to and (home_score - away_score) >= 2
            away_wins_set = away_score >= first_to and (away_score - home_score) >= 2
            
            if home_wins_set:
                home_sets_won += 1
            elif away_wins_set:
                away_sets_won += 1
            else:
                return False, f"Set {set_idx + 1} is not finished yet"
            
            # Check if match is already decided
            if home_sets_won >= sets_needed:
                return True, f"Match over: {home_sets_won}-{away_sets_won} sets"
            if away_sets_won >= sets_needed:
                return True, f"Match over: {home_sets_won}-{away_sets_won} sets"
        
        return False, ""
    
    def _create_widgets(self):
        """Create the form widgets."""
        # Title
        title = ttk.Label(self.frame, text="Enter Match Results", 
                         font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        # Info label for format
        if self.set_formats:
            format_str = " | ".join([f"Set {i+1}: First to {f}" for i, f in enumerate(self.set_formats)])
            info_label = ttk.Label(self.frame, text=f"Format: {format_str}", 
                                  font=("Arial", 9), foreground="gray")
            info_label.pack(pady=5)
        
        # Canvas with scrollbar for better UX
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Container for match entries
        container = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=container, anchor="nw")
        
        # Bind mousewheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _on_container_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        container.bind("<Configure>", _on_container_configure)
        
        # Create entry rows for each game
        unplayed_count = 0
        played_count = 0
        
        for game_idx, game in enumerate(self.games):
            teams = game[0]
            score_sets = game[1]
            is_played = len(score_sets) > 0  # If score_sets is not empty, it's already played
            
            if is_played:
                played_count += 1
                if self.show_played:
                    self._add_game_row(container, game_idx, teams, score_sets, is_played)
            else:
                unplayed_count += 1
                self._add_game_row(container, game_idx, teams, score_sets, is_played)
        
        # Show summary if games are hidden
        if played_count > 0 and not self.show_played:
            summary = ttk.Label(container, text=f"({played_count} played games hidden)", 
                              foreground="gray", font=("Arial", 9))
            summary.pack(pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10, fill=tk.X)
        
        ttk.Button(button_frame, text="Submit", 
                  command=self._handle_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Empty", 
                  command=self._handle_clear).pack(side=tk.LEFT, padx=5)
    
    def _add_game_row(self, container: tk.Widget, game_idx: int, teams: List[str], 
                      score_sets: List, is_played: bool):
        """Add a single game entry row."""
        row_frame = ttk.LabelFrame(container, text=f"Game {game_idx + 1} - {teams[0]} vs {teams[1]}", 
                                   relief=tk.RIDGE, padding=10)
        row_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # If already played, display the scores
        if is_played:
            sets_text = " | ".join([f"Set {i+1}: {set_score[0]}-{set_score[1]}" 
                                    for i, set_score in enumerate(score_sets)])
            ttk.Label(row_frame, text=f"Scores: {sets_text}", foreground="green", 
                     font=("Arial", 10)).pack(anchor="w", pady=5)
            
            match_over, reason = self._is_match_over(score_sets)
            if match_over:
                ttk.Label(row_frame, text=reason, foreground="darkgreen", 
                         font=("Arial", 9, "italic")).pack(anchor="w")
            
            self.game_entries.append({
                'game_idx': game_idx,
                'teams': teams,
                'score_sets': score_sets,
                'is_played': True,
                'entry_fields': [],
                'error_labels': []
            })
        else:
            # Create entry fields for score sets
            entry_fields = []
            error_labels = []
            
            # Create input fields for each set format
            num_sets = len(self.set_formats) if self.set_formats else 5
            
            for set_num in range(num_sets):
                set_frame = ttk.Frame(row_frame)
                set_frame.pack(fill=tk.X, pady=3)
                
                set_label_text = f"Set {set_num + 1}"
                if self.set_formats and set_num < len(self.set_formats):
                    set_label_text += f" (1st to {self.set_formats[set_num]}):"
                else:
                    set_label_text += ":"
                
                ttk.Label(set_frame, text=set_label_text, width=20).pack(side=tk.LEFT, padx=5)
                
                home_var = tk.StringVar()
                away_var = tk.StringVar()
                
                home_entry = ttk.Entry(set_frame, textvariable=home_var, width=5)
                home_entry.pack(side=tk.LEFT, padx=2)
                
                ttk.Label(set_frame, text="-").pack(side=tk.LEFT, padx=2)
                
                away_entry = ttk.Entry(set_frame, textvariable=away_var, width=5)
                away_entry.pack(side=tk.LEFT, padx=2)
                
                # Error label for this set
                error_label = ttk.Label(set_frame, text="", foreground="red", font=("Arial", 8))
                error_label.pack(side=tk.LEFT, padx=5)
                
                entry_fields.append({
                    'set_num': set_num,
                    'home_var': home_var,
                    'away_var': away_var,
                    'error_label': error_label
                })
                error_labels.append(error_label)
            
            self.game_entries.append({
                'game_idx': game_idx,
                'teams': teams,
                'score_sets': score_sets,
                'is_played': False,
                'entry_fields': entry_fields,
                'error_labels': error_labels
            })
    
    def _handle_submit(self):
        """Handle form submission and return updated games list."""
        updated_games = []
        all_valid = True
        
        for entry in self.game_entries:
            game_idx = entry['game_idx']
            teams = entry['teams']
            
            if entry['is_played']:
                # Already played - keep as is
                updated_games.append([teams, entry['score_sets']])
            else:
                # Unplayed - collect entered scores
                score_sets = []
                game_valid = True
                
                for set_entry in entry['entry_fields']:
                    home_score_str = set_entry['home_var'].get().strip()
                    away_score_str = set_entry['away_var'].get().strip()
                    error_label = set_entry['error_label']
                    
                    # Both empty is OK - skip this set
                    if not home_score_str and not away_score_str:
                        error_label.config(text="")
                        continue
                    
                    # Both must be provided if one is
                    if not home_score_str or not away_score_str:
                        error_label.config(text="Both scores required")
                        game_valid = False
                        all_valid = False
                        continue
                    
                    try:
                        home_score = int(home_score_str)
                        away_score = int(away_score_str)
                        
                        # Validate the score
                        is_valid, error_msg = self._is_valid_score(home_score, away_score, set_entry['set_num'])
                        
                        if not is_valid:
                            error_label.config(text=error_msg)
                            game_valid = False
                            all_valid = False
                            continue
                        
                        error_label.config(text="")
                        score_sets.append([home_score, away_score])
                        
                        # Check if match is already decided after this set
                        match_over, reason = self._is_match_over(score_sets)
                        if match_over:
                            # Match is decided - remaining sets shouldn't be filled
                            error_label.config(text="Match already decided")
                            break
                    
                    except ValueError:
                        error_label.config(text="Invalid number")
                        game_valid = False
                        all_valid = False
                        continue
                
                updated_games.append([teams, score_sets])
        
        if all_valid:
            self.on_submit(updated_games)
        else:
            print("Validation errors - please check scores")
    
    def _handle_clear(self):
        """Clear all unplayed game entries."""
        for entry in self.game_entries:
            if not entry['is_played']:
                for set_entry in entry['entry_fields']:
                    set_entry['home_var'].set("")
                    set_entry['away_var'].set("")
                    set_entry['error_label'].config(text="")
    
    def get_frame(self) -> tk.Widget:
        """Return the frame for packing into a parent widget."""
        return self.frame


#Final, easy function 
def enter_games(games,show_played=False,set_formats=[25,25,15]):
    root = tk.Tk()
    root.title("Match Results Entry")
    root.geometry("800x700")

    entry_form = MatchResultsEntry(root, games, 
                                   show_played=False)
    
    root.mainloop()

    def override_by_first(a, b):
    # Build lookup from list B
        lookup = {tuple(row[0]): row for row in b}

        # Replace rows in A when key exists in B
        return [lookup.get(tuple(row[0]), row) for row in a]

    return override_by_first(games,entry_form.results)



##################################################################

# Example usage
if __name__ == "__main__":
    def example_callback(results):
        print("\nUpdated games:")
        for i, game in enumerate(results, 1):
            teams = game[0]
            scores = game[1]
            if scores:
                sets_str = " | ".join([f"{s[0]}-{s[1]}" for s in scores])
                print(f"  Game {i}: {teams[0]} vs {teams[1]} -> {sets_str}")
            else:
                print(f"  Game {i}: {teams[0]} vs {teams[1]} -> (empty)")
    
    root = tk.Tk()
    root.title("Match Results Entry")
    root.geometry("800x700")
    
    # Example games (mix of played and unplayed)
    # Volleyball best-of-3, first to 11 (or 15 in tiebreak)
    games = [
        [["Team A", "Team B"], []],  # Unplayed
        [["Team C", "Team D"], [[11, 9], [11, 8]]],  # Already played (Team C wins 2-0)
        [["Team E", "Team F"], []],  # Unplayed
        [["Team G", "Team H"], [[11, 13], [9, 11]]],  # Already played (Team H wins 2-0)
        #[["Team I", "Team J"], []],  # Unplayed
        [["Team K", "Team L"], [[11, 7], [10, 12], [11, 9]]],  # Already played (Team K wins 2-1)
    ]
    
    # Set format: first to 11 for sets 1-2, first to 15 for set 3 (if needed)
    # set_formats = [11, 11, 15]
    
    entry_form = MatchResultsEntry(root, games, 
                                   show_played=False)
    
    root.mainloop()

    #print(entry_form.games)