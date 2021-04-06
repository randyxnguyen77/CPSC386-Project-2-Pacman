# import pygame
# import pygame.freetype
# from pygame.sprite import Sprite
# from pygame.rect import Rect
# import constants
# # from text import Text
# from enum import Enum
# from pygame.sprite import RenderUpdates
#
#
# class GameState(Enum):
#     QUIT = -1
#     TITLE = 0
#     PLAY = 1
#
#
# def title_screen(screen):
#     buttons = [start_btn, quit_btn]
#     return game_loop(screen, buttons)
#
#
# def game_loop(screen, buttons):
#     while True:
#         mouse_up = False
#         for event in pygame.event.get():
#             if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
#                 mouse_up = True
#             screen.fill(constants.WHITE)
#
#             for button in buttons:
#                 ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
#                 if ui_action is not None:
#                     return ui_action
#
#         buttons.draw(screen)
#         pygame.display.flip()
