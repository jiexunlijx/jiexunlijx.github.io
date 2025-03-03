import pandas as pd

def main():
    # Read the Excel file
    df = pd.read_excel('votes.xlsx', sheet_name='Sheet1')
    
    # Clean the data: remove duplicate votes for each voter
    for index, row in df.iterrows():
        seen = set()
        unique_votes = []
        for vote in row[1:]:  # Skip the 'Voter' column
            if vote not in seen and pd.notna(vote):
                unique_votes.append(vote)
                seen.add(vote)
        # Pad the row with None to match the original length
        df.iloc[index, 1:] = unique_votes + [None] * (len(row) - 1 - len(unique_votes))
    
    # Get the list of unique candidates
    candidates = pd.unique(df.iloc[:, 1:].values.ravel())
    candidates = [c for c in candidates if pd.notna(c)]
    
    # Ask for the number of seats
    num_seats = int(input("Enter the number of seats available: "))
    
    # Calculate the Droop quota
    total_votes = len(df)
    quota = (total_votes // (num_seats + 1)) + 1
    
    # Define the Ballot class to manage voter preferences and vote value
    class Ballot:
        def __init__(self, preferences):
            self.preferences = [p for p in preferences if pd.notna(p)]
            self.value = 1.0
        
        def current_candidate(self, hopefuls):
            # Return the highest-ranked candidate who is still hopeful
            for pref in self.preferences:
                if pref in hopefuls:
                    return pref
            return None  # Ballot is exhausted
    
    # Create a list of Ballot objects from the DataFrame
    ballots = [Ballot(row[1:]) for _, row in df.iterrows()]
    
    # Initialize election state
    hopefuls = set(candidates)  # Candidates still in the running
    elected = []  # List of elected candidates
    
    # STV process
    while len(elected) < num_seats and hopefuls:
        # Count votes for each hopeful candidate
        votes = {c: 0.0 for c in hopefuls}
        for ballot in ballots:
            candidate = ballot.current_candidate(hopefuls)
            if candidate:
                votes[candidate] += ballot.value
        
        if not votes:
            break
        
        # Find the candidate with the most votes
        max_votes = max(votes.values())
        if max_votes >= quota:
            # Elect the candidate with the most votes
            candidate = max(votes, key=votes.get)
            elected.append(candidate)
            hopefuls.remove(candidate)
            
            # Calculate surplus and transfer votes
            total_votes_candidate = votes[candidate]
            surplus = total_votes_candidate - quota
            transfer_ratio = surplus / total_votes_candidate if total_votes_candidate > 0 else 0
            for ballot in ballots:
                # If the ballot's current candidate (including the just-elected one) is the elected candidate
                if ballot.current_candidate(hopefuls | {candidate}) == candidate:
                    ballot.value *= transfer_ratio  # Reduce the ballot's value and transfer
        else:
            # Eliminate the candidate with the fewest votes
            min_votes = min(votes.values())
            candidates_with_min_votes = [c for c in hopefuls if votes[c] == min_votes]
            # Break ties by eliminating the first candidate in the list
            candidate = candidates_with_min_votes[0]
            hopefuls.remove(candidate)
            # Ballots will automatically reassign to the next hopeful candidate in the next round
    
    # Display the results
    print("Elected candidates in order of election:")
    for i, candidate in enumerate(elected, 1):
        print(f"{i}. {candidate}")

if __name__ == "__main__":
    main()