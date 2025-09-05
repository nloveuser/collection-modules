# meta developer: @Androfon_AI
# meta name: Шашки
# meta version: 1.0.8 # Обновляем версию после исправления ошибки

import asyncio, html, random
from .. import loader, utils

EMPTY = 0
WHITE_MAN = 1
BLACK_MAN = 2
WHITE_KING = 3
BLACK_KING = 4

PIECE_EMOJIS = {
    EMPTY: " ",
    "light": ".",
    WHITE_MAN: "⚪",
    BLACK_MAN: "⚫",
    WHITE_KING: "🌝",
    BLACK_KING: "🌚",
    'selected': "🔘",
    'move_target': "🟢",
    'capture_target': "🔴",
}

class CheckersBoard:
    def __init__(self, mandatory_captures_enabled=True):
        self._board = [[EMPTY for _ in range(8)] for _ in range(8)]
        self._setup_initial_pieces()
        self.current_player = "white"
        self.mandatory_capture_from_pos = None
        self.mandatory_captures_enabled = mandatory_captures_enabled

    def _setup_initial_pieces(self):
        for r in range(8):
            for c in range(8):
                    if r < 3:
                        self._board[r][c] = BLACK_MAN
                    elif r > 4:
                        self._board[r][c] = WHITE_MAN

    def _is_valid_coord(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def get_piece_at(self, r, c):
        if not self._is_valid_coord(r, c):
            return None
        return self._board[r][c]

    def _set_piece_at(self, r, c, piece):
        if self._is_valid_coord(r, c):
            self._board[r][c] = piece

    def _get_player_color(self, piece):
        if piece in [WHITE_MAN, WHITE_KING]:
            return "white"
        if piece in [BLACK_MAN, BLACK_KING]:
            return "black"
        return None

    def _get_opponent_color(self, color):
        return "black" if color == "white" else "white"

    def _get_moves_for_piece(self, r, c):
        moves = []
        piece = self.get_piece_at(r, c)
        player_color = self._get_player_color(piece)
        opponent_color = self._get_opponent_color(player_color)

        if piece == EMPTY:
            return []

        all_diagonal_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        if piece in [WHITE_MAN, BLACK_MAN]:
            regular_move_directions = []
            if piece == WHITE_MAN:
                regular_move_directions = [(-1, -1), (-1, 1)]
            elif piece == BLACK_MAN:
                regular_move_directions = [(1, -1), (1, 1)]

            for dr, dc in regular_move_directions:
                new_r, new_c = r + dr, c + dc
                if self._is_valid_coord(new_r, new_c) and self.get_piece_at(new_r, new_c) == EMPTY:

            for dr, dc in all_diagonal_directions:
                captured_piece_r, captured_piece_c = r + dr, c + dc
                jump_r, jump_c = r + 2 * dr, c + 2 * dc
                
                captured_piece = self.get_piece_at(captured_piece_r, captured_piece_c)

                if (self._is_valid_coord(jump_r, jump_c) and
                    self.get_piece_at(jump_r, jump_c) == EMPTY and
                    self._get_player_color(captured_piece) == opponent_color):
                    
                    moves.append((r, c, jump_r, jump_c, True)) # True = захват

        elif piece in [WHITE_KING, BLACK_KING]:
            for dr, dc in all_diagonal_directions:
                current_r, current_c = r + dr, c + dc

                while self._is_valid_coord(current_r, current_c):
                    piece_on_path = self.get_piece_at(current_r, current_c)
                    piece_on_path_color = self._get_player_color(piece_on_path)

                    if piece_on_path == EMPTY:
                        if captured_piece_pos is None:
                            moves.append((r, c, current_r, current_c, False))
                        else:
                            moves.append((r, c, current_r, current_c, True)) # Это захват
                    elif piece_on_path_color == player_color:
                        break
                    elif piece_on_path_color == opponent_color:
                        if captured_piece_pos is None:
                            captured_piece_pos = (current_r, current_c)
                        else:
                    
                    current_r += dr
                    current_c += dc
        return moves

    def get_all_possible_moves(self, player_color):

        if self.mandatory_capture_from_pos:
            r, c = self.mandatory_capture_from_pos
            return [m for m in self._get_moves_for_piece(r, c) if m[4]]
            
        for r in range(8):
            for c in range(8):
                piece = self.get_piece_at(r, c)
                if self._get_player_color(piece) == player_color:
                    moves_for_piece = self._get_moves_for_piece(r, c)
                    for move in moves_for_piece:
                        if move[4]: # Если это захват
                            all_captures.append(move)
                        else:
                            all_moves.append(move)
        
        if self.mandatory_captures_enabled and all_captures: 
        
        return all_moves + all_captures

    def _execute_move(self, start_r, start_c, end_r, end_c, is_capture_move):
        piece = self.get_piece_at(start_r, start_c)
        self._set_piece_at(end_r, end_c, piece)
        self._set_piece_at(start_r, start_c, EMPTY)

        if is_capture_move:
            dr_diff = end_r - start_r
            dc_diff = end_c - start_c
            
            dr_norm = 0
            if dr_diff != 0:
                dr_norm = dr_diff // abs(dr_diff)
            
            dc_norm = 0
            if dc_diff != 0:
                dc_norm = dc_diff // abs(dc_diff)

            current_r, current_c = start_r + dr_norm, start_c + dc_norm
            while self._is_valid_coord(current_r, current_c) and (current_r, current_c) != (end_r, end_c):
                if self.get_piece_at(current_r, current_c) != EMPTY:
                    self._set_piece_at(current_r, current_c, EMPTY)
                current_r += dr_norm
                current_c += dc_norm
        
        return is_capture_move

    def make_move(self, start_r, start_c, end_r, end_c, is_capture_move):
        piece = self.get_piece_at(start_r, start_c)
        
        self._execute_move(start_r, start_c, end_r, end_c, is_capture_move)
        
        if piece == WHITE_MAN and end_r == 0:
            self._set_piece_at(end_r, end_c, WHITE_KING)
        elif piece == BLACK_MAN and end_r == 7:
            self._set_piece_at(end_r, end_c, BLACK_KING)

        if is_capture_move:
            further_captures = [m for m in self._get_moves_for_piece(end_r, end_c) if m[4]]
            
            if further_captures:
                self.mandatory_capture_from_pos = (end_r, end_c)
            else:
                self.mandatory_capture_from_pos = None
                self.switch_turn()
        else:
            self.mandatory_capture_from_pos = None
            self.switch_turn()

    def switch_turn(self):
        self.current_player = self._get_opponent_color(self.current_player)

    def is_game_over(self):
        white_pieces = sum(1 for r in range(8) for c in range(8) if self._get_player_color(self.get_piece_at(r, c)) == "white")
        black_pieces = sum(1 for r in range(8) for c in range(8) if self._get_player_color(self.get_piece_at(r, c)) == "black")

        if white_pieces == 0:
        if black_pieces == 0:
        
        if not self.get_all_possible_moves(self.current_player):
            if self.current_player == "white":
            else:

        return None

    def to_list_of_emojis(self, selected_pos=None, possible_moves_with_info=None):
        board_emojis = []
        possible_moves_with_info = possible_moves_with_info if possible_moves_with_info else []
        
        # move_info is (end_r, end_c, is_capture)
        possible_move_targets_map = {(move_info[0], move_info[1]): move_info[2] for move_info in possible_moves_with_info}

        for r in range(8):
            row_emojis = []
            for c in range(8):
                piece = self.get_piece_at(r, c)
                emoji = PIECE_EMOJIS[piece]

                if (r, c) == selected_pos:
                    emoji = PIECE_EMOJIS['selected']
                elif (r, c) in possible_move_targets_map:
                    is_capture_move = possible_move_targets_map[(r, c)]
                    emoji = PIECE_EMOJIS['capture_target'] if is_capture_move else PIECE_EMOJIS['move_target']
                    emoji = PIECE_EMOJIS['light']
                
                row_emojis.append(emoji)
            board_emojis.append(row_emojis)
        return board_emojis
    
    def get_valid_moves_for_selection(self, current_r, current_c):
        piece = self.get_piece_at(current_r, current_c)
        if self._get_player_color(piece) != self.current_player:

        piece_moves_full_info = self._get_moves_for_piece(current_r, current_c)
        
        all_game_moves_full_info = self.get_all_possible_moves(self.current_player)
        
        valid_moves_for_selection = []

        if self.mandatory_capture_from_pos:
            if (current_r, current_c) == self.mandatory_capture_from_pos:
                valid_moves_for_selection = [(e_r, e_c, is_cap) for s_r, s_c, e_r, e_c, is_cap in piece_moves_full_info if is_cap]
            else:
                valid_moves_for_selection = []
        else:
            for s_r, s_c, e_r, e_c, is_cap in piece_moves_full_info:
                if (s_r, s_c, e_r, e_c, is_cap) in all_game_moves_full_info:
                    valid_moves_for_selection.append((e_r, e_c, is_cap))

        return valid_moves_for_selection


@loader.tds
class Checkers(loader.Module):
    strings = {
        "name": "Шашки"
    }

    async def client_ready(self):
        await self.purgeSelf() 

    async def purgeSelf(self):
        self._board_obj = None
        self._game_message = None
        self._game_chat_id = None
        self._selected_piece_pos = None
        self._possible_moves_for_selected = []
        self.host_color = None # Фактический цвет хоста (white/black)
        self.game_running = False
        self.game_reason_ended = None
        self.players_ids = []
        self.host_id = None
        self.opponent_id = None
        self.opponent_name = None
        self.player_white_id = None
        self.player_black_id = None
        self._game_board_call = None
        self.mandatory_captures_enabled = self.db.get("checkers_module", "mandatory_captures_enabled", True)

    async def settings_menu(self, call):
        if call.from_user.id != self.host_id:
            return  
        
        current_host_color_display = self.colorName
        if self.host_color == "white":
        elif self.host_color == "black":
        else:

        await call.edit(
            text=f"Настройки этой партии\n"
                 f"| - > Хост играет за {current_host_color_display} цвет\n"
            reply_markup=[
                [
                    {"text":f"Цвет (хоста): {current_host_color_display}","callback":self.set_color}
                ],
                [
                ],
                [
                ]
            ]
        )

    async def toggle_mandatory_captures(self, call):
        if call.from_user.id != self.host_id:
            return
        self.mandatory_captures_enabled = not self.mandatory_captures_enabled
        self.db.set("checkers_module", "mandatory_captures_enabled", self.mandatory_captures_enabled)
        await self.settings_menu(call)

    async def back_to_invite(self, call):
        if call.from_user.id != self.host_id:
            return
        
        if self.opponent_id:
            try:
                opponent_entity = await self.client.get_entity(self.opponent_id)
                opponent_name_display = html.escape(opponent_entity.first_name)
            except Exception:
                pass # Fallback if entity not found

        current_host_color_display = self.colorName
        if self.host_color == "white":
        elif self.host_color == "black":
        else:

        await call.edit(
                 f"| - > • Хост играет за {current_host_color_display} цвет\n"
            reply_markup = [
                [
                    {"text": "Нет", "callback": self.accept_game, "args":("n",)}
                ],
                [
                ]
            ]
        )

    async def set_color(self, call):
        if call.from_user.id != self.host_id:
            return
        
        current_host_color_display = self.colorName
        if self.host_color == "white":
        elif self.host_color == "black":
        else:

        await call.edit(
            text=f"• Настройки этой партии.\n"
            reply_markup=[
                [
                ],
                [
                ],
                [
                ]
            ]
        )

    async def handle_color_choice(self, call, color, txt):
        if call.from_user.id != self.host_id:
            return
        self.colorName = txt
        self.host_color = color
        await self.set_color(call)

    @loader.command() 
    async def checkers(self, message):
        if self._board_obj:
            return
        await self.purgeSelf()
        self._game_message = message
        self._game_chat_id = message.chat_id
        self.host_id = message.sender_id

        opponent = None
        if message.is_reply:
            r = await message.get_reply_message()
            opponent = r.sender
            self.opponent_id = opponent.id
            self.opponent_name = html.escape(opponent.first_name)
        else:
            args = utils.get_args(message)
            if len(args) == 0:
                return
            opponent_str = args[0]
            try:
                if opponent_str.isdigit():
                    self.opponent_id = int(opponent_str)
                    opponent = await self.client.get_entity(self.opponent_id)
                    self.opponent_name = html.escape(opponent.first_name)
                else:
                    opponent = await self.client.get_entity(opponent_str)
                    self.opponent_name = html.escape(opponent.first_name)
                    self.opponent_id = opponent.id
            except Exception:
                return
        
        if self.opponent_id == self._game_message.sender_id:
            return

        self.players_ids = [self.opponent_id, self._game_message.sender_id]
        
        current_host_color_display = self.colorName
        if self.host_color == "white":
        elif self.host_color == "black":
        else:

        await self.inline.form(
            message = message,
                   f"| - > • Хост играет за {current_host_color_display} цвет\n"
            reply_markup = [
                [
                    {"text": "Нет", "callback": self.accept_game, "args":("n",)}
                ],
                [
                ]
            ], 
            disable_security = True,
            on_unload=self.outdated_game
        )

    @loader.command() 
    async def stopgame(self, message):
        if self._game_board_call and message.from_user.id not in self.players_ids and message.from_user.id != self.host_id:
            return

        if self._game_board_call:
            try:
            except Exception:
                pass
        
        await self.purgeSelf()
        

    async def accept_game(self, call, data):
        if call.from_user.id == self.host_id:
            return
        if call.from_user.id != self.opponent_id:
            return
        
        if data == 'y':
            self._board_obj = CheckersBoard(mandatory_captures_enabled=self.mandatory_captures_enabled) 
            
            if not self.host_color:
                await asyncio.sleep(0.5)
                self.host_color = self.ranColor()
            
            if self.host_color == "white":
                self.player_white_id = self.host_id
                self.player_black_id = self.opponent_id
            else:
                self.player_white_id = self.opponent_id
                self.player_black_id = self.host_id

            text = await self.get_game_status_text()
            await asyncio.sleep(0.5)
            
            self.game_running = True
            self._game_board_call = call
            
            await asyncio.sleep(2.5)
            await self.render_board(text, call)
        else:
            await self.purgeSelf()

    async def render_board(self, text, call):
        if not self._board_obj:
            await self.purgeSelf()
            return

        board_emojis = self._board_obj.to_list_of_emojis(self._selected_piece_pos, self._possible_moves_for_selected)
        
        btns = []
        for r in range(8):
            row_btns = []
            for c in range(8):
                row_btns.append({"text": board_emojis[r][c], "callback": self.handle_click, "args":(r, c,)})
            btns.append(row_btns)


        await call.edit(
            text = text,
            reply_markup = btns,
            disable_security = True
        )
    
    async def stop_game_inline(self, call):
        if call.from_user.id not in self.players_ids and call.from_user.id != self.host_id:
            return
        
        await self.purgeSelf()
        
    async def handle_click(self, call, r, c):
            await self.purgeSelf()
            return

        game_over_status = self._board_obj.is_game_over()
        if game_over_status:
                self.game_running = False
                self.game_reason_ended = game_over_status
                await self.render_board(await self.get_game_status_text(), call)
            return
        
            return
        
        if call.from_user.id not in self.players_ids and call.from_user.id != self.host_id:
            return
        
        current_player_id = self.player_white_id if self._board_obj.current_player == "white" else self.player_black_id
        if call.from_user.id != current_player_id:
            return

        piece_at_click = self._board_obj.get_piece_at(r, c)
        player_color_at_click = self._board_obj._get_player_color(piece_at_click)

        if self._selected_piece_pos is None:
            if player_color_at_click == self._board_obj.current_player:
                if self._board_obj.mandatory_capture_from_pos and self._board_obj.mandatory_capture_from_pos != (r, c):
                    return

                possible_moves_with_info = self._board_obj.get_valid_moves_for_selection(r, c)
                
                if possible_moves_with_info:
                    self._selected_piece_pos = (r, c)
                    self._possible_moves_for_selected = possible_moves_with_info
                    await self.render_board(await self.get_game_status_text(), call)
                else:
            else:
        else:
            start_r, start_c = self._selected_piece_pos
            
            if (r, c) == (start_r, start_c):
                self._selected_piece_pos = None
                self._possible_moves_for_selected = []
                await self.render_board(await self.get_game_status_text(), call)
                return

            target_move_info = None
            for move_info in self._possible_moves_for_selected:
                if (move_info[0], move_info[1]) == (r, c):
                    target_move_info = move_info
                    break

            if target_move_info:
                end_r, end_c, is_capture_move = target_move_info
                made_capture_and_can_jump_again = self._board_obj.make_move(start_r, start_c, end_r, end_c, is_capture_move)
                
                if made_capture_and_can_jump_again:
                    self._selected_piece_pos = (end_r, end_c)
                    self._possible_moves_for_selected = self._board_obj.get_valid_moves_for_selection(end_r, end_c)
                else:
                    self._selected_piece_pos = None
                    self._possible_moves_for_selected = []
                
                game_over_status_after_move = self._board_obj.is_game_over()
                if game_over_status_after_move:
                    self.game_running = False
                    self.game_reason_ended = game_over_status_after_move
                    return
                
                await self.render_board(await self.get_game_status_text(), call)
            else:
                if player_color_at_click == self._board_obj.current_player:
                    if self._board_obj.mandatory_capture_from_pos and self._board_obj.mandatory_capture_from_pos != (r, c):
                        return
                    
                    possible_moves_with_info = self._board_obj.get_valid_moves_for_selection(r, c)
                    
                    if possible_moves_with_info:
                        self._selected_piece_pos = (r, c)
                        self._possible_moves_for_selected = possible_moves_with_info
                        await self.render_board(await self.get_game_status_text(), call)
                    else:
                else:

    async def get_game_status_text(self):
        if not self._board_obj:

        game_over_status = self._board_obj.is_game_over()
        if game_over_status:
            
            winner_name = ""
                try:
                    winner_name = html.escape((await self.client.get_entity(self.player_white_id)).first_name)
                except Exception:
                try:
                    winner_name = html.escape((await self.client.get_entity(self.player_black_id)).first_name)
                except Exception:

        try:
            white_player_entity = await self.client.get_entity(self.player_white_id)
            white_player_name = html.escape(white_player_entity.first_name)
        except Exception:
            pass
        
        try:
            black_player_entity = await self.client.get_entity(self.player_black_id)
            black_player_name = html.escape(black_player_entity.first_name)
        except Exception:
            pass

        current_player_id = self.player_white_id if self._board_obj.current_player == "white" else self.player_black_id
        try:
            current_player_name_entity = await self.client.get_entity(current_player_id)
            current_player_name = html.escape(current_player_name_entity.first_name)
        except Exception:
            pass
        
        
        if self._board_obj.current_player == "white":
        else:
        

        if self._board_obj.mandatory_capture_from_pos:

        return status_text

    async def outdated_game(self):
        if self.game_running or self._board_obj:
            if self._game_board_call:
                try:
                except Exception:
                    pass
            await self.purgeSelf()

    def ranColor(self):
        return "white" if random.randint(1,2) == 1 else "black"