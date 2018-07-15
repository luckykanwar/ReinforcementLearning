import numpy as np

LENGTH = 3

class Agent:
	def __init__(self, eps=0.1, alpha=0.5):
		self.eps = eps
		self.alpha = alpha
		self.verbose = False
		self.state_history = []

	def setV(self, V):
		self.V = V

	def set_symbol(self, sym):
		self.sym = sym

	def set_verbose(self, v):
		self.verbose = v

	def reset_history(self):
		self.state_history = []

	def take_action(self, env):
		r = np.random.rand()
		best_state = None	
		if r < self.eps:
			if self.verbose:
				print("Taking a random action")

			possible_moves = []
			for i in range(LENGTH):
				for j in range(LENGTH):
					if env.is_empty(i, j):
						possible_moves.append((i,j))
			idx = np.random.choice(len(possible_moves))
			next_move = possible_moves[idx]
		else:
			pos2value = {}
			next_move = None
			best_value = -1
			for i in range(LENGTH):
				for j in range(LENGTH):
					if env.is_empty(i,j):
						env.board[i,j] = self.sym
						state = env.get_state()
						env.board[i,j] = 0
						pos2value[(i,j)] = self.V[state]
						if self.V[state] > best_value:
							best_value = self.V[state]
							best_state = state
							next_move = (i,j)

							#print("self.V[state]: ",self.V[state])
							#print("next_move: ",next_move)

			if self.verbose:
				print("Taking a greedy action")
				for i in range(LENGTH):
					print("------------------")	
					for j in range(LENGTH):
						if env.is_empty(i,j):
							print(" %.2f|" % pos2value[(i,j)], end="")
						else:
							print("  ", end ="")
							if env.board[i,j] == env.x:
								print("x  |", end="")
							elif env.board[i,j] == env.o:
								print("o  |", end="")
							else:
								print("  |", end="")
					print("")
				print("------------------")

	def update_state_history(self, s):
		self.state_history.append(s)

	def update(self, env):
		reward = env.reward(self.sym)
		target = reward
		for prev in reversed(self.state_history):
			value = self.V[prev] + self.alpha*(target - self.V[prev])
			self.V[prev] =  value
			target = value
		self.reset_history()

class Environment:
	
	def __init__(self):
		self.board = np.zeros((LENGTH, LENGTH))
		self.x = -1
		self.o = 1
		self.winner = None
		self.ended = False
		self.num_states = 3**(LENGTH*LENGTH)

	def is_empty(self, i, j):
		if(self.board[i,j] == 0):
			return True
		else:	
			return False
	
	def reward(self, sym):
		if not self.game_over():
			return 0
		
		if self.winner == sym:
			return 1
		else:
			return 0
	
	def get_state(self): 
		# this function sort of returns a heuristic value
		k = 0
		h = 0
		for i in range(LENGTH):
			for j in range(LENGTH):
				if self.board[i,j] == 0:
					v = 0
				elif self.board[i,j] == self.x:
					v = 1
				elif self.board[i,j] == self.o:
					v = 2
				h += (3**k) * v
				k += 1
		return h

	def game_over(self, force_recalculate = False):
		if not force_recalculate and self.ended:
			return self.ended
		
		for i in range(LENGTH):
			for player in (self.x, self.o):
				if self.board[i].sum() == player*LENGTH:
					self.winner = player
					self.ended = True
					return True	

		for j in range(LENGTH):
			for player in (self.x, self.o):
				if self.board[:,j].sum() == player*LENGTH:
					self.winner = player
					self.ended = True
					return True	

		for player in (self.x, self.o):
				if self.board.trace() == player*LENGTH:
					self.winner = player
					self.ended = True
					return True	
	
		for player in (self.x, self.o):
				if self.board.trace() == player*LENGTH:
					self.winner = player
					self.ended = True
					return True	
				
				if np.fliplr(self.board).trace() == player*LENGTH:
					self.winner = player
					self.ended = True
					return True	
		
		if np.all((self.board == 0) == False):
			self.winner = None
			self.ended = True
			return True	
		
		self.winner = None
		return False

	def is_draw(self):
		return self.ended and self.winner is None

	def draw_board(self):
		for i in range(LENGTH):
			print("----------------")
			for j in range(LENGTH):
				print(" ", end="")
				if self.board[i,j] == self.x:
					print("x ", end="")
				elif self.board[i,j] == self.o:
					print("o ", end="")
				else:
					print("  ", end="")
			print("")
		print("----------------")

class Human:
	def __init__(self):
		pass
	
	def set_symbo(self, sym):
		self.sym = sym

	def take_action(self, env):
		while True:
			move = input("Enter coordinates i,j for your next move: ")
			i,j = move.split(',')
			i = int(i)
			j = int(j)

			if env.is_empty(i,j):
				env.board[i,j] = self.sym
				break

	def update(self, env):
		pass

	def update_state_history(self, s):
		pass

def get_state_hash_and_winner(env, i=0, j=0):
	results = []

	for v in (0, env.x, env.o):
		env.board[i,j] = v
		if j == 2:
			if i == 2:
				state = env.get_state()
				ended = env.game_over(force_recalculate = True)
				winner = env.winner
				results.append((state, winner, ended))
			else:
				results += get_state_hash_and_winner(env, i+1, 0)
		else:
			results += get_state_hash_and_winner(env, i, j+1)
	return results

def initialV_x(env, state_winner_triples):
	V = np.zeros(env.num_states)
	for state, winner, ended in state_winner_triples:
		if ended:
			if winner == env.x:
				v = 1
			else:
				v = 0
		else:
			v = 0.5
		V[state] = v
	return V

def initialV_o(env, state_winner_triples):
	V = np.zeros(env.num_states)
	for state, winner, ended in state_winner_triples:
		if ended:
			if winner == env.o:
				v = 1
			else:
				v = 0
		else:
			v = 0.5
		V[state] = v
	return V

def play_game(p1, p2, env, draw=False):
  	# loops until the game is over
	current_player = None
	while not env.game_over():
		# alternate between players
		# p1 always starts first
		if current_player == p1:
			current_player = p2
		else:
			current_player = p1

		# draw the board before the user who wants to see it makes a move
		if draw:
			if draw == 1 and current_player == p1:
				env.draw_board()
			if draw == 2 and current_player == p2:
				env.draw_board()

		# current player makes a move
		current_player.take_action(env)

		# update state histories
		state = env.get_state()
		p1.update_state_history(state)
		p2.update_state_history(state)

	if draw:
		env.draw_board()

	# do the value function update
	p1.update(env)
	p2.update(env)

if __name__ == '__main__':
	 # train the agent
	p1 = Agent()
	p2 = Agent()

	# set initial V for p1 and p2
	env = Environment()
	state_winner_triples = get_state_hash_and_winner(env)

	#print(state_winner_triples)
	Vx = initialV_x(env, state_winner_triples)
	p1.setV(Vx)
	Vo = initialV_o(env, state_winner_triples)
	p2.setV(Vo)

	# give each player their symbol
	p1.set_symbol(env.x)
	p2.set_symbol(env.o)

	T = 10000
	for t in range(T):
		if t % 200 == 0:
			print(t)
		play_game(p1, p2, Environment(), draw = 2)
	
'''
	# play human vs. agent
	# do you think the agent learned to play the game well?
	human = Human()
	human.set_symbol(env.o)
	while True:
		p1.set_verbose(False)
		play_game(p1, human, Environment(), draw=2)
		# I made the agent player 1 because I wanted to see if it would
		# select the center as its starting move. If you want the agent
		# to go second you can switch the human and AI.
		answer = input("Play again? [Y/n]: ")
		if answer and answer.lower()[0] == 'n':
		break
'''