import random

class CTheGame():
    def __init__(self, n_player:int=3, card_weight_threshold:int=95):
        if n_player>5:
            n_player=5
        if n_player<1:
            n_player=1
        self.n_player=n_player
        self.card_deck=list(range(2,100))
        self.shuffle_card_deck()
        self.give_cards()
        self.stack={0:[1], 1:[1], 2:[100], 3:[100]}
        self.n_iterations=0
        self.active_player=0
        self.stop=False
        self.card_weight_threshold=card_weight_threshold

    def give_cards(self):
        self.player={}
        for n in range(self.n_player):
            self.player[n]=[]
            for jj in range(self._get_cards_per_player()):
                self.player[n].append(self.card_deck.pop(-1))

    def _get_cards_per_player(self):
        n_cards=[8, 7, 6, 6, 6]
        return(n_cards[self.n_player-1])

    def shuffle_card_deck(self):
        random.shuffle(self.card_deck)

    def __str__(self):
        out_str='Card deck: '
        for c in self.card_deck:
            out_str=out_str+ str(c)+', '
        out_str=out_str[:-2]+'\n'
        for jj in range(4):
            out_str+=f'Stack {jj}: ' 
            for c in self.stack[jj]:
                out_str+=str(c)+', '
            out_str=out_str[:-2]+'\n'
        for jj in range(self.n_player):
            out_str+=f'Player {jj}: ' 
            for c in self.player[jj]:
                out_str+=str(c)+', '
            out_str=out_str[:-2]+'\n'
        n_cards_rem=self._calc_total_no_of_remaining_cards()
        out_str+=f'number of iterations: {self.n_iterations}, active player: {self.active_player}, cards remaining: {n_cards_rem}'
        return(out_str)

    def _calc_total_no_of_remaining_cards(self):
        n_cards=0
        for kk in range(self.n_player):
            n_cards+=len(self.player[kk])
        n_cards+=len(self.card_deck)
        return n_cards

    def _check_stack_min_diff(self, min_difference, hand, upwards=True):
        min_val=100
        min_stack=0
        min_ix=0
        if upwards:
            for kk in range(2):
                for jj in range(len(hand)):
                    if abs(min_difference[kk][jj])<min_val and min_difference[kk][jj]>0:
                        min_val=min_difference[kk][jj]
                        min_stack=kk
                        min_ix=jj
        else:
            for kk in range(2):
                for jj in range(len(hand)):
                    if abs(min_difference[kk+2][jj])<min_val and min_difference[kk+2][jj]<0:
                        min_val=abs(min_difference[kk+2][jj])
                        min_stack=kk+2
                        min_ix=jj
        return min_val, min_stack, min_ix


    def _calc_min_difference(self, hand:dict):
        min_difference={}
        # Check for distance of ten
        for jj in range(4):
            min_difference[jj]=[kk-self.stack[jj][-1] for kk in hand]
        return min_difference

    def _check_if_card_within_threshold(self, hand:dict):
        min_diff=self._calc_min_difference(hand)
        for jj in min_diff:
            for kk in min_diff[jj]:
                if abs(kk)<=self.diff_thresh:
                    # print(self)
                    return True
        return False

    def play_card_metric(self, hand:dict):
        min_difference=self._calc_min_difference(hand)
        for jj in range(4):
            if jj in (0,1):
                if -10 in min_difference[jj]:
                    ix=min_difference[jj].index(-10)
                    self.stack[jj].append(hand.pop(ix))
                    return True
            if jj in (2,3):
                if 10 in min_difference[jj]:
                    ix=min_difference[jj].index(10)
                    self.stack[jj].append(hand.pop(ix))
                    return True
        # print(min_difference)
        min_val1, min_stack1, min_ix1=self._check_stack_min_diff(min_difference, hand, upwards=True)
        min_val2, min_stack2, min_ix2=self._check_stack_min_diff(min_difference, hand, upwards=False)
        if min_val1<=min_val2 and min_val1!=100:
            self.stack[min_stack1].append(hand.pop(min_ix1))
        elif min_val2<min_val1 and min_val2!=100:
            self.stack[min_stack2].append(hand.pop(min_ix2))
        else:
            return False
        return True

    def calc_card_weight_function(self, hand:dict):
        weights={}
        for kk in range(2):
            weights[kk]=[0 for card in hand]
            top_card=self.stack[kk][-1]
            for ix, card in enumerate(hand):
                card_diff=top_card-card
                # check if we have a difference of -10 or 10
                if card_diff==10:
                    weights[kk][ix]=100
                else:
                    if card_diff>0:
                        weights[kk][ix]=0
                    else:
                        weights[kk][ix]=100+card_diff
        for kk in range(2):
            weights[kk+2]=[0 for card in hand]
            top_card=self.stack[kk+2][-1]
            for ix, card in enumerate(hand):
                card_diff=top_card-card
                # check if we have a difference of -10 or 10
                if card_diff==-10:
                    weights[kk+2][ix]=100
                else:
                    if card_diff<0:
                        weights[kk+2][ix]=0
                    else:
                        weights[kk+2][ix]=100-card_diff
        return weights

    def get_card_and_stack_of_best_weight(self, weights):
        best_card_weight=0
        best_card_ix=0
        best_card_stack=0
        for sw in weights:
            for ic, w in enumerate(weights[sw]):
                if w>best_card_weight:
                    best_card_weight=w
                    best_card_stack=sw
                    best_card_ix=ic
        return best_card_weight, best_card_ix, best_card_stack


    def play_card_of_best_weight(self, best_card_weight, best_card_ix, best_card_stack):
        hand=self.player[self.active_player]
        if best_card_weight==0:
            # no playable card in hand
            return False
        self.stack[best_card_stack].append(hand.pop(best_card_ix))
        return True

    def play_card(self, strategy='metric'):
        hand=self.player[self.active_player]
        if len(hand)==0:
            return True
        if strategy=='metric':
            return self.play_card_metric(hand)
        else:
            weights=self.calc_card_weight_function(hand)
            best_card_weight, best_card_ix, best_card_stack=self.get_card_and_stack_of_best_weight(weights)
            return self.play_card_of_best_weight(best_card_weight, best_card_ix, best_card_stack)
            
    def refresh_hand(self):
        hand=self.player[self.active_player]
        while len(hand)<self._get_cards_per_player():
            if len(self.card_deck)>0:
                hand.append(self.card_deck.pop(-1))
            else:
                break

    def next_iteration(self):
        self.n_iterations+=1
        if not self.play_card(strategy='weight'):
            self.stop=True
        if len(self.card_deck)>0:
            if not self.play_card(strategy='weight'):
                self.stop=True
        # while self._check_if_card_within_threshold(self.player[self.active_player]):
        #     if not self.play_card(strategy='weight'):
        #         self.stop=True
        #         break
        while True:
            weights=self.calc_card_weight_function(self.player[self.active_player])
            best_card_weight, best_card_ix, best_card_stack=self.get_card_and_stack_of_best_weight(weights)
            if best_card_weight>self.card_weight_threshold:
                if not self.play_card(strategy='weight'):
                    self.stop=True
                    break
            else:
                break

            
        if self._calc_total_no_of_remaining_cards()==0:
            self.stop=True
        if not self.stop:
            self.refresh_hand()
            self.active_player=self.n_iterations%self.n_player

if __name__=="__main__":
    n_games=0
    play_games=True
    while play_games:
        n_games+=1
        cg=CTheGame(n_player=5, card_weight_threshold=95)
        # print(cg)
        while not cg.stop:
            cg.next_iteration()
            if cg.n_iterations>100:
                cg.stop=True
        # print(cg)
        if cg._calc_total_no_of_remaining_cards()==0:
            play_games=False
        if n_games%100==0:
            print(cg)
            print(n_games)
    # cg=CTheGame()
    # print(cg)
    # while not cg.stop:
    #     cg.next_iteration()
    #     if cg.n_iterations>100:
    #         cg.stop=True
    print(cg)
    print(n_games)
