"""
Game logic management
"""

from bson import ObjectId
from fastapi import WebSocket

from dice_be.models.games import GameData, Code, GameProgression, GameRules, PlayerData
from dice_be.models.users import User
from dice_be.models.game_events import Event, PlayerLeave, PlayerReady, ReadyConfirm
from dice_be.managers.connection import ConnectionManager


class GameManager:
    """
    Manages the progression of a single game
    """
    def __init__(self, code: Code, game_rules: GameRules):
        self.game_data = GameData(event='game_update', code=code, rules=game_rules)
        self.player_mapping: dict[ObjectId, PlayerData] = {}
        self.connection_manager = ConnectionManager()

    async def handle_json(self, player: User, data: dict):
        """
        Handles a json received from the player's connection
        :param player: The player who sent the data
        :param data: Parsed json object
        """
        event = Event.parse_obj(data).__root__

        match event:
            case GameData():
                await self.handle_game_update(player, event)
            case PlayerLeave():
                await self.handle_player_leave(player)
            case PlayerReady():
                await self.handle_player_ready(player, event)

    async def handle_connect(self, player: User, connection: WebSocket):
        # Add the connection so we can send data
        self.connection_manager.add_connection(player, connection)

        # This means that the player is new (not reconnecting)
        if player.id not in self.player_mapping:
            self.player_mapping[player.id] = PlayerData(id=player.id, name=player.name)
            self.game_data.add_player(player)

            await self.connection_manager.broadcast(
                self.game_data.player_update_json(),
                exclude=(player,)
            )

        # Send the lobby data to the player
        await self.connection_manager.send(player, self.game_data.lobby_json({'players'}))

    async def handle_player_leave(self, player: User):
        await self.connection_manager.disconnect(player)
        player_data = self.player_mapping.pop(player.id)
        self.game_data.players.remove(player_data)
        await self.connection_manager.broadcast(self.game_data.player_update_json())

    async def handle_disconnect(self, player: User):
        """
        Handle a websocket disconnect
        :param player: The player that disconnected
        """
        self.connection_manager.remove_connection(player)

    async def handle_game_update(self, player: User, data: GameData):
        pass

    async def handle_game_start(self):
        self.game_data.progression = GameProgression.IN_GAME
        await self.connection_manager.broadcast(self.game_data.progression_update_json())

    async def handle_player_ready(self, player: User, data: PlayerReady):
        # Player is setting himself unready
        if not data.ready:
            self.player_mapping[player.id].ready = data.ready
            self.player_mapping[player.id].right_player_id = None
            self.player_mapping[player.id].left_player_id = None
            return

        # Player is setting himself ready, check for validity of right and left players
        for game_player in self.game_data.players:
            # Skip self check
            if player == game_player:
                continue
            if game_player.right_player_id == data.player_on_right:
                right_player = self.player_mapping[ObjectId(data.player_on_right)]
                error = f'{right_player.name} is already to the right of {game_player.name}'
                break
            elif game_player.left_player_id == data.player_on_left:
                left_player = self.player_mapping[ObjectId(data.player_on_left)]
                error = f'{left_player.name} is already to the left of {game_player.name}'
                break
        else:  # No break = no player was found to be to the left/right of 2 people at the same time
            self.player_mapping[player.id].ready = data.ready
            return await self.connection_manager.send(player, ReadyConfirm(success=True).json(exclude_none=True))

        return await self.connection_manager.send(player, ReadyConfirm(
            success=False,
            error=error
        ))



