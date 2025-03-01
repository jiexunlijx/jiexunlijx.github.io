import pandas as pd

def irv_ranking(ballots):
    """
    Process ballots using Instant Runoff Voting to produce a full ranking.
    
    Args:
        ballots (list): List of ballots, where each ballot is a list of candidates in order of preference.
    
    Returns:
        list: Ranking of candidates in decreasing order of preference.
    """
    candidates = set()
    for ballot in ballots:
        candidates.update(ballot)
    eliminated = []
    while len(candidates) > 1:
        # Count first-preference votes
        first_prefs = {c: 0 for c in candidates}
        for ballot in ballots:
            for c in ballot:
                if c in candidates:
                    first_prefs[c] += 1
                    break
        total_votes = sum(first_prefs.values())
        if total_votes == 0:
            break
        max_votes = max(first_prefs.values())
        if max_votes > total_votes / 2:
            winner = max(first_prefs, key=first_prefs.get)
            break
        else:
            # Eliminate candidates with fewest votes (sorted for consistency)
            min_votes = min(first_prefs.values())
            to_eliminate = sorted([c for c in candidates if first_prefs[c] == min_votes])
            for c in to_eliminate:
                candidates.remove(c)
            eliminated.extend(to_eliminate)
            # Update ballots by removing eliminated candidates
            ballots = [[c for c in b if c in candidates] for b in ballots]
    else:
        # If one candidate remains
        winner = list(candidates)[0] if candidates else None
    # Construct ranking: winner first, then reverse elimination order
    ranking = [winner] + eliminated[::-1] if winner else eliminated[::-1]
    return ranking

def find_irv_winner(ballots, candidates):
    """
    Find a single winner using IRV for the STV process.
    
    Args:
        ballots (list): Current ballots with remaining candidates.
        candidates (set): Set of candidates still in contention.
    
    Returns:
        str or None: The winning candidate, or None if no winner.
    """
    while len(candidates) > 1:
        first_prefs = {c: 0 for c in candidates}
        for ballot in ballots:
            for c in ballot:
                if c in candidates:
                    first_prefs[c] += 1
                    break
        total_votes = sum(first_prefs.values())
        if total_votes == 0:
            return None
        max_votes = max(first_prefs.values())
        if max_votes > total_votes / 2:
            return max(first_prefs, key=first_prefs.get)
        else:
            min_votes = min(first_prefs.values())
            to_eliminate = sorted([c for c in candidates if first_prefs[c] == min_votes])
            for c in to_eliminate:
                candidates.remove(c)
            ballots = [[c for c in b if c in candidates] for b in ballots]
    return list(candidates)[0] if candidates else None

def stv_ranking(ballots):
    """
    Process ballots using a sequential STV approach to produce a full ranking.
    
    Args:
        ballots (list): List of ballots, where each ballot is a list of candidates in order of preference.
    
    Returns:
        list: Ranking of candidates in decreasing order of preference.
    """
    candidates = set()
    for ballot in ballots:
        candidates.update(ballot)
    ranking = []
    while candidates:
        # Create current ballots with only remaining candidates
        current_ballots = [[c for c in ballot if c in candidates] for ballot in ballots]
        winner = find_irv_winner(current_ballots, candidates.copy())
        if winner:
            ranking.append(winner)
            candidates.remove(winner)
        else:
            break
    return ranking

def main():
    """Main function to read the Excel file, process votes, and display results."""
    # Read the Excel file
    try:
        df = pd.read_excel('votes.xlsx')
    except FileNotFoundError:
        print("Error: 'votes.xlsx' file not found.")
        return
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Verify the first column is 'Voter'
    if df.columns[0] != "Voter":
        print("Error: First column must be 'Voter'.")
        return

    # Extract choice columns (all columns after 'Voter')
    choice_columns = df.columns[1:]
    ballots = []
    for index, row in df.iterrows():
        # Collect non-null preferences for each voter
        ballot = [row[col] for col in choice_columns if pd.notna(row[col])]
        ballots.append(ballot)

    # Prompt user to choose voting system
    system = input("Choose the voting system (IRV or STV): ").strip().upper()
    if system == "IRV":
        ranking = irv_ranking(ballots)
    elif system == "STV":
        ranking = stv_ranking(ballots)
    else:
        print("Invalid choice. Please enter 'IRV' or 'STV'.")
        return

    # Display the results
    if ranking:
        print("Ranking in decreasing order of preference:")
        for i, candidate in enumerate(ranking, 1):
            print(f"{i}. {candidate}")
    else:
        print("No valid ranking could be determined.")

if __name__ == "__main__":
    main()