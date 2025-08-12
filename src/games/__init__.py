# Animated games (Telegram native)
from src.games.coinflip_animated import coinflip_callback
from src.games.dice_animated import dice_command_wrapper as dice_command, dice_callback
from src.games.slots_animated import slots_command_wrapper as slots_command, slots_callback
from src.games.darts_animated import darts_command_wrapper as darts_command, darts_callback
from src.games.bowling_animated import bowling_command_wrapper as bowling_command, bowling_callback
from src.games.wheel_animated import wheel_callback
from src.games.basketball_animated import basketball_command_wrapper as basketball_command, basketball_callback
from src.games.football_animated import football_command_wrapper as football_command, football_callback

# Webapp games don't need callback imports - they're handled through the webapp
