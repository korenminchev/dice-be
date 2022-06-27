"""
Game logic management
"""
import asyncio

from bson import ObjectId
from fastapi import WebSocket

from dice_be.models.games import GameData, Code, GameProgression, GameRules, JOKER_DICE, PlayerData
from dice_be.models.users import User
from dice_be.models.game_events import Event, PlayerLeave, PlayerReady, ReadyConfirm, GameStart, RoundEnd, RoundStart, Accusation, \
    AccusationType
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
            case PlayerLeave():
                await self.handle_player_leave(player)
            case PlayerReady():
                await self.handle_player_ready(player, event)
            case Accusation():
                await self.handle_accusation(player, event)

    async def handle_connect(self, player: User, connection: WebSocket):
        # Add the connection so we can send data
        self.connection_manager.add_connection(player, connection)

        # This means that the player is new (not reconnecting)
        if player.id not in self.player_mapping:
            self.player_mapping[player.id] = self.game_data.add_player(player)

            await self.connection_manager.broadcast(
                self.game_data.player_update_json(),
                exclude=player
            )

        # Send the lobby data to the player
        await self.connection_manager.send(player, self.game_data.lobby_json())

        if self.game_data.progression == GameProgression.IN_GAME:
            await self.connection_manager.send(player, RoundStart.from_player(self.player_mapping[player.id]))

    async def handle_player_leave(self, player: User):
        await self.connection_manager.disconnect(player)
        player_data = self.player_mapping.pop(player.id)
        self.game_data.players.remove(player_data)
        await self.connection_manager.broadcast(self.game_data.player_update_json(), exclude=player)

    async def handle_disconnect(self, player: User):
        """
        Handle a websocket disconnect
        :param player: The player that disconnected
        """
        self.connection_manager.remove_connection(player)

    async def start_game(self):
        # Initialize all players dice count
        for player in self.game_data.players:
            player.current_dice_count = self.game_data.rules.initial_dice_count

        self.game_data.progression = GameProgression.IN_GAME
        await self.connection_manager.broadcast(GameStart(rules=self.game_data.rules).json())
        await self.start_round()

    def check_position(self, player: User, data: PlayerReady) -> tuple[bool, str | None]:
        # Player is setting himself ready, check for validity of right and left players
        for other_player in self.player_mapping.values():
            # Skip checking against the same players or against unready players
            if str(player.id) == str(other_player.id) or not other_player.ready:
                continue

            if other_player.right_player_id == data.right_player_id:
                right_player = self.player_mapping[ObjectId(data.right_player_id)]
                return False, f'{right_player.name} is already to the right of {other_player.name}'
            elif other_player.left_player_id == data.left_player_id:
                left_player = self.player_mapping[ObjectId(data.left_player_id)]
                return False, f'{left_player.name} is already to the left of {other_player.name}'

        return True, None

    async def handle_player_ready(self, player: User, data: PlayerReady):
        success = False
        if data.ready:
            success, error = self.check_position(player, data)
            await self.connection_manager.send(player, ReadyConfirm(
                success=success,
                error=error
            ).json(exclude_none=True))

        player_data: PlayerData = self.player_mapping[player.id]
        player_data.ready = success
        player_data.right_player_id = data.right_player_id
        player_data.left_player_id = data.left_player_id

        if all(player.ready for player in self.player_mapping.values()):
            await self.start_game()

    async def start_round(self):
        for player in self.game_data.players:
            player.roll_dice()

        await asyncio.gather(
            *(self.connection_manager.send(
                player, self.game_data.round_start_json()) for player in self.game_data.players)
        )

        await asyncio.gather(
            *(self.connection_manager.send(
                player, RoundStart.from_player(player)) for player in self.game_data.players)
        )

    async def handle_accusation(self, player: User, event: Accusation):
        correct_accusation = False
        accuser = self.player_mapping[ObjectId(player.id)]
        accused_player = self.player_mapping[ObjectId(event.accused_player)]

        total_accused_count, total_joker_count = self.count_dice(event.dice_value)
        total_count = total_accused_count + total_joker_count
        claimed_count = event.dice_count

        match event.type:
            case AccusationType.Standard:
                correct_accusation = claimed_count > total_count

            case AccusationType.Exact:
                correct_accusation = claimed_count != total_count

            case AccusationType.Paso:
                correct_accusation = not accused_player.is_paso()

        if correct_accusation:
            winner, loser = accuser, accused_player
            accused_player.current_dice_count -= 1
        else:
            loser, winner = accuser, accused_player
            accuser.current_dice_count -= 1

        await self.connection_manager.broadcast(RoundEnd.from_context(
            accusation=event,
            correct_accusation=correct_accusation,
            dice_count=total_accused_count,
            joker_count=total_joker_count,
            game_data=self.game_data,
            winner=winner,
            loser=loser,
        ))

        await self.start_round()

    def count_dice(self, value: int) -> tuple[int, int]:
        dice_count = sum(player.dice.count(value) for player in self.game_data.players) if value != JOKER_DICE else 0
        joker_count = sum(player.dice.count(JOKER_DICE) for player in self.game_data.players)
        return dice_count, joker_count
