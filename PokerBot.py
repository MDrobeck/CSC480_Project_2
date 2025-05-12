import random
import time
from collections import *
import string

# --- Constants ---
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


def create_deck():
    return [(rank, suit) for suit in SUITS for rank in RANKS]


def deal(deck):
    hands = [[] for _ in range(2)]
    cards_dealt = 0
    while cards_dealt < 2:
        for i in range(2):
            hands[i].append(deck.pop())
        cards_dealt += 1
    return hands, deck


'''
Evaluates the hand based on a scale of 0-1000
High Card: rank of card alone, next highest card, next highest card, next highest card, lowest card
Pair: 100 + rank of pair, highest kicker, mid kicker, lowest kicker
2 Pair: 200 + rank of highest pair, rank of other pair, kicker
trips: 300 + rank of trips, kicker rank, kicker rank
straight: 400 + highest rank in straight (handles 14, 2, 3, 4, 5 as worst straight)
flush: 500 + highest rank, next highest, next highest, next highest, next highest to handle ties
full house: 600 + highest rank, 2 pair rank
quads: 700 + rank, kicker
straight flush: 800 + highest rank in straight
royal flush: 900 (auto win p much best hand)'''


def evaluate_hand(hand, community_cards):
    card_ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                  '8': 8, '9': 9, '10': 10, 'J': 11,
                  'Q': 12, 'K': 13, 'A': 14}

    card_suits = {'Hearts': 15, 'Clubs': 16, 'Spades': 17, 'Diamonds': 18}

    all_cards = hand + community_cards

    # card ranks to numbers
    hand_ranks = []
    for card in all_cards:
        rank = card[0]
        hand_ranks.append(card_ranks[rank])  # list of ranks in hand and board

    hand_suits = []
    for card in all_cards:
        suit = card[1]
        hand_suits.append(card_suits[suit])  # list of ranks in hand and board

    cr = Counter(hand_ranks)  # count number of each rank
    cs = Counter(hand_suits)

    # sorted by count then rank, highest first for both
    mult_card_rank = sorted(cr.items(),
                            key=lambda x: (-x[1], -x[0]))  # multiple cards for pairs, 2 pair, trips, quads etc.
    mult_card_suit = sorted(cs.items(),
                            key=lambda x: (-x[1], -x[0]))  # multiple suits for flush, royal, straight flush.

    ranks_only = [item[0] for item in mult_card_rank]  # for hands that only care about ranks i.e: pair, 2 pair etc

    print(mult_card_suit)
    print(mult_card_rank)
    def safe_get_ranks(n):  # index error fix
        result = ranks_only[:min(n, len(ranks_only))] + [0] * max(0, n - len(ranks_only))
        return result[:n]  # get num of cards we have

    royal = False
    SF = False
    flush = False
    flush_suit = None
    straight = False

    if mult_card_suit[0][1] >= 5:
        flush = True
        flush_suit = mult_card_suit[0][0]

    indiv_ranks = sorted(set(hand_ranks), reverse=True)

    if 14 in indiv_ranks:  # Ace counts as high and low for straights
        indiv_ranks.append(1)

    s_high_card = 0
    straight_cards = []
    if len(indiv_ranks) >= 5:
        for i in range(len(indiv_ranks) - 4):
            s_cards = indiv_ranks[i:i + 5]
            if s_cards[0] - s_cards[4] == 4 and len(set(s_cards)) == 5:
                straight = True
                s_high_card = s_cards[0]
                straight_cards = [s_cards[0], s_cards[1], s_cards[2], s_cards[3], s_cards[4]]
                break  # found the highest straight, going more would hurt your hand


    if flush and straight:  # for royals and straight flushes
        flush_cards = []
        for card in all_cards:
            rank = card_ranks[card[0]]
            suit = card_suits[card[1]]
            if suit == flush_suit and rank in straight_cards:  # to see if flush cards math up with straight cards
                flush_cards.append(rank)

        flush_cards = sorted(set(flush_cards), reverse=True)  # sort for easier straight calcs
        if len(flush_cards) >= 5:
            top_cards = flush_cards[:5]
            if top_cards[0] - top_cards[4] == 4 and len(set(top_cards)) == 5:
                if set(top_cards) == {10, 11, 12, 13, 14}:  # if cards are 10-A and a flush
                    royal = True
                else:  # if cards arent 10-A
                    SF = True

    if royal:
        return 900, 0, 0, 0, 0, 0  # both players cant have a royal - physically impossible - auto win

    if SF:
        r1 = s_high_card
        return 800, r1, 0, 0, 0, 0  # only need highest card rank, others dont matter

    if mult_card_rank[0][1] == 4:  # Quads
        r1, r2 = safe_get_ranks(2)
        return 700, r1, r2, 0, 0, 0  # only need 2 ranks

    if mult_card_rank[0][1] == 3 and mult_card_rank[1][1] >= 2:  # Full House
        r1, r2 = safe_get_ranks(2)
        return 600, r1, r2, 0, 0, 0  # only need 2 ranks

    if flush_suit:
        flush_cards = [card for card in all_cards if card[1] == flush_suit]
        flush_ranks = sorted([card_ranks[card[0]] for card in flush_cards], reverse=True)
        while len(flush_ranks) < 5:
            flush_ranks.append(0)
        return 500, *flush_ranks[:5]  # flush - every rank needed for kickers

    if straight:
        r1 = s_high_card
        return 400, r1, 0, 0, 0, 0  # really only need 1 rank - highest card in straight - others dont really matter

    if mult_card_rank[0][1] == 3:  # Trips
        r1, r2, r3 = safe_get_ranks(3)
        return 300, r1, r2, r3, 0, 0  # Padding with extra zeros

    if mult_card_rank[0][1] == 2 and mult_card_rank[1][1] == 2:  # Two Pair
        r1, r2, r3 = safe_get_ranks(3)
        return 200, r1, r2, r3, 0, 0  # only need 3 ranks

    if mult_card_rank[0][1] == 2:  # Pair
        r1, r2, r3, r4 = safe_get_ranks(4)
        return 100, r1, r2, r3, r4, 0  # need 4 ranks

    # High card
    r = safe_get_ranks(5)
    while len(r) < 5:  # 5 cards
        r.append(0)
    return (0,) + tuple(r[:5])  # take best 5


def simulate_win_probability(my_hand, known_community, deck, time_limit=10.0):
    start_time = time.time()
    wins = 0
    total = 0

    while time.time() - start_time < time_limit:  # start 10 second timer
        # temp deck so actual deck is not lost
        temp_deck = deck.copy()

        # remove cards that are already in play
        for card in my_hand + known_community:
            if card in temp_deck:
                temp_deck.remove(card)

        # guess what cards opponent can potentially have

        opponent_hand = []
        for _ in range(2):
            card = random.choice(temp_deck)
            opponent_hand.append(card)
            temp_deck.remove(card)

        # sim the board for rest of game
        remaining = 5 - len(known_community)

        simulated_community = known_community.copy()
        for _ in range(remaining):
            card = random.choice(temp_deck)
            simulated_community.append(card)
            temp_deck.remove(card)

        # eval both simulated hands
        my_score = evaluate_hand(my_hand, simulated_community)
        opp_score = evaluate_hand(opponent_hand, simulated_community)

        # compare and add to wins
        if my_score > opp_score:
            wins += 1
        elif my_score == opp_score:
            wins += 0.5

        total += 1

    # see if should fold based on UBC1
    return wins / total if total > 0 else 0


def make_decision(my_hand, community_cards, deck, phase_name):
    print(f"\n--------- {phase_name} ----------")
    print(f"{phase_name} Board:", community_cards)
    win_prob = simulate_win_probability(my_hand, community_cards, deck, 10)
    print(f"Estimated Win Probability: {win_prob:.2%}")
    if win_prob >= 0.5:
        print("stay")
        return "stay"
    else:
        print("fold")
        return "fold"


def play_game():

    deck = create_deck()
    random.shuffle(deck)
    hands, deck = deal(deck)
    my_hand = hands[0]
    opponent_hand = hands[1]
    print("My Hand:", my_hand)

    community_cards = []

    if make_decision(my_hand, community_cards, deck, "Pre-Flop") == "fold":
        print("Bot folded Pre-Flop.")
        return

    community_cards += [deck.pop() for _ in range(3)]

    if make_decision(my_hand, community_cards, deck, "Flop") == "fold":
        print("Bot folded on Turn.")
        return

    community_cards.append(deck.pop())

    if make_decision(my_hand, community_cards, deck, "Turn") == "fold":
        print("Bot folded on River.")
        return

    # --- River ---
    community_cards.append(deck.pop())
    print("\n--------- River ----------")
    print("Final Community Cards:", community_cards)
    print("My Hand:", my_hand)
    print("Opponent's Hand:", opponent_hand)

    # Evaluate both hands
    my_score = evaluate_hand(my_hand, community_cards)
    opp_score = evaluate_hand(opponent_hand, community_cards)

    # Map score category to hand name
    hand_names = {
        900: "Royal Flush",
        800: "Straight Flush",
        700: "Four of a Kind",
        600: "Full House",
        500: "Flush",
        400: "Straight",
        300: "Three of a Kind",
        200: "Two Pair",
        100: "One Pair",
        0: "High Card"
    }

    def hand_type(score): #get hand name based on number, rest will mess it up
        return hand_names.get(score[0])

    print(f"\nMy hand rank: {hand_type(my_score)}")

    print(f"\nOpponent hand rank: {hand_type(opp_score)}")

    if my_score > opp_score:
        print("\nResult: You win")
    elif my_score < opp_score:
        print("\nResult: You Lost")
    else:
        print("\nResult: Push")


if __name__ == "__main__":
    play_game()
