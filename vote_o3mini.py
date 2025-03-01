#!/usr/bin/env python3
import argparse
import pandas as pd
from collections import defaultdict

def read_ballots_from_excel(filename):
    """
    Reads an .xlsx file where the first column is 'Voter' and the remaining columns are ranked choices.
    Returns a list of ballots, with each ballot being a list of candidate names (as strings), omitting missing values.
    """
    df = pd.read_excel(filename)
    # Assumes the first column header is 'Voter'
    ballots = []
    for _, row in df.iterrows():
        # Take all columns after 'Voter' and ignore NaNs.
        ballot = [str(candidate) for candidate in row[1:] if pd.notna(candidate)]
        ballots.append(ballot)
    return ballots

def instant_runoff(ballots):
    """
    Implements a simplified Instant Runoff Voting algorithm.
    It repeatedly counts each ballot’s first valid (non-eliminated) choice and eliminates the candidate with the fewest votes.
    The complete elimination order is tracked and finally reversed so the winner is listed first and the weakest candidate last.
    """
    # Determine the starting set of candidates from all ballots.
    candidates = set()
    for ballot in ballots:
        candidates.update(ballot)
    candidates = list(candidates)

    elimination_order = []  # Will store eliminated candidates in order (first eliminated is worst)
    # Make a working copy of ballots (so that candidates can be removed)
    working_ballots = [ballot[:] for ballot in ballots]

    while candidates:
        vote_counts = {candidate: 0 for candidate in candidates}
        for ballot in working_ballots:
            # Count the first candidate in the ballot that is still active.
            for candidate in ballot:
                if candidate in candidates:
                    vote_counts[candidate] += 1
                    break

        total_votes = sum(vote_counts.values())
        if total_votes == 0:
            break

        # If only one candidate remains, add it and break.
        if len(candidates) == 1:
            elimination_order.append(candidates[0])
            candidates.remove(candidates[0])
            break

        # Check if a candidate has an outright majority.
        majority_candidate = None
        for candidate, count in vote_counts.items():
            if count > (total_votes / 2):
                majority_candidate = candidate
                break

        if majority_candidate:
            elimination_order.append(majority_candidate)
            candidates.remove(majority_candidate)
            # Remove the candidate from all ballots.
            for ballot in working_ballots:
                if majority_candidate in ballot:
                    ballot.remove(majority_candidate)
            continue

        # Eliminate candidate with the fewest votes (tie-breaker: alphabetical order)
        min_votes = min(vote_counts.values())
        tied_candidates = [c for c, count in vote_counts.items() if count == min_votes]
        candidate_to_eliminate = sorted(tied_candidates)[0]
        elimination_order.append(candidate_to_eliminate)
        candidates.remove(candidate_to_eliminate)
        # Remove the eliminated candidate from ballots.
        for ballot in working_ballots:
            if candidate_to_eliminate in ballot:
                ballot.remove(candidate_to_eliminate)

    # Reverse the elimination order so that the last candidate eliminated (winner) is first.
    ranking = list(reversed(elimination_order))
    return ranking

def droop_quota(total_votes, seats):
    """
    Computes the Droop quota used in STV counting.
    Formula: quota = (total_votes // (seats + 1)) + 1
    """
    return (total_votes // (seats + 1)) + 1

def single_transferable_vote(ballots, seats=1):
    """
    A simplified implementation of the Single Transferable Vote algorithm.
    Each ballot is given an initial weight of 1. Candidates who reach the Droop quota are elected,
    and any surplus votes from an elected candidate are transferred fractionally.
    If no candidate reaches the quota, the candidate with the fewest votes is eliminated and their votes are transferred.
    The elimination and election sequence is tracked to produce a final ordering from highest support downward.
    """
    # Identify all candidates on the ballots
    candidates = set()
    for ballot in ballots:
        candidates.update(ballot)
    candidates = list(candidates)

    elected = []
    elimination_order = []  # Record order of election/elimination
    # Prepare ballots as tuples of (ballot_list, current_weight)
    working_ballots = [(ballot[:], 1) for ballot in ballots]
    total_votes = sum(weight for _, weight in working_ballots)
    quota = droop_quota(total_votes, seats)

    def count_votes():
        counts = defaultdict(float)
        for ballot, weight in working_ballots:
            for candidate in ballot:
                if candidate in candidates and candidate not in elected:
                    counts[candidate] += weight
                    break
        return counts

    while len(elected) < seats and candidates:
        vote_counts = count_votes()
        # Check if any candidate meets or exceeds the quota.
        elected_this_round = None
        for candidate, count in vote_counts.items():
            if count >= quota:
                elected.append(candidate)
                elimination_order.append(candidate)
                candidates.remove(candidate)
                elected_this_round = candidate
                # Transfer the surplus from this candidate.
                surplus = count - quota
                if surplus > 0:
                    new_working_ballots = []
                    for ballot, weight in working_ballots:
                        if ballot and ballot[0] == candidate:
                            # Transfer a fraction of the weight (surplus divided by total votes for candidate)
                            transfer_fraction = surplus / count
                            new_ballot = ballot[1:]
                            new_weight = weight * transfer_fraction
                            if new_ballot:
                                new_working_ballots.append((new_ballot, new_weight))
                        else:
                            new_working_ballots.append((ballot, weight))
                    working_ballots = new_working_ballots
                break

        if elected_this_round is not None:
            continue

        # If no candidate reached quota, eliminate candidate with fewest votes (alphabetical tie-breaker)
        if vote_counts:
            min_votes = min(vote_counts.values())
            tied = [c for c, v in vote_counts.items() if v == min_votes]
            candidate_to_eliminate = sorted(tied)[0]
            elimination_order.append(candidate_to_eliminate)
            candidates.remove(candidate_to_eliminate)
            # Remove eliminated candidate from ballots so votes can transfer.
            new_working_ballots = []
            for ballot, weight in working_ballots:
                if ballot and ballot[0] == candidate_to_eliminate:
                    new_ballot = ballot[1:]
                    new_working_ballots.append((new_ballot, weight))
                else:
                    new_working_ballots.append((ballot, weight))
            working_ballots = new_working_ballots
        else:
            break

    # If seats are still not filled, sort remaining candidates by current vote count.
    if len(elected) < seats and candidates:
        remaining = sorted(candidates, key=lambda c: vote_counts.get(c, 0), reverse=True)
        for candidate in remaining:
            elected.append(candidate)
            elimination_order.append(candidate)

    # For ranking output, we return the elimination/election order reversed:
    ranking = list(reversed(elimination_order))
    return ranking

def main():
    parser = argparse.ArgumentParser(
        description="Ranked Choice Voting Tally Script: Reads an Excel (.xlsx) file with ballots."
    )
    parser.add_argument("filename", help="Path to the .xlsx file containing ballots.")
    parser.add_argument(
        "-s", "--system",
        choices=["irv", "stv"],
        default="irv",
        help="Voting system to use: 'irv' (Instant Runoff Voting) or 'stv' (Single Transferable Vote)."
    )
    parser.add_argument(
        "--seats",
        type=int,
        default=1,
        help="Number of seats for STV (default=1). For IRV, only one winner is determined."
    )
    args = parser.parse_args()

    ballots = read_ballots_from_excel(args.filename)
    if not ballots:
        print("No ballots were found in the file.")
        return

    if args.system == "irv":
        ranking = instant_runoff(ballots)
    else:
        ranking = single_transferable_vote(ballots, seats=args.seats)

    print("Final Ranking (highest preference first):")
    for i, candidate in enumerate(ranking, start=1):
        print(f"{i}. {candidate}")

if __name__ == "__main__":
    main()
