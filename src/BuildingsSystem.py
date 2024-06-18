from typing import List
import pygame

import global_vars
from Bulding import Building

pygame.init()

def create_buildings_and_determine_x_pos():
    buildings: List[Building] = [Building(c['floors'], c['elevators']) for c in global_vars.GAME_LAYOUT]
    buildings_pos_x =  []
    x_start = 0
    for building in buildings:
        buildings_pos_x.append([x_start, x_start + building.surface_width])
        x_start += building.surface_width

    return list(zip(buildings, buildings_pos_x))

class BuildingsSystem():
    def __init__(self) -> None:
        # create buildings
        self.buildings_with_pos_x = create_buildings_and_determine_x_pos()

        # create scrollable surface
        self.surface_width = max(
            self.buildings_with_pos_x[-1][1][1],
            global_vars.GAME_MIN_SCREEN_WIDTH_PX
            )
        self.surface_height = max(
            [global_vars.GAME_MIN_SCREEN_HEIGHT_PX, 
             *[b.surface_height for [b, pos] in self.buildings_with_pos_x]
             ])
        self.scrolable_surface = pygame.Surface([self.surface_width, self.surface_height])

        # create screen
        self.screen_width = min(global_vars.GAME_MAX_SCREEN_WIDTH_PX, self.surface_width)
        self.screen_height = min(self.surface_height, global_vars.GAME_MAX_SCREEN_HEIGHT_PX)
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])

        # scroll bounds
        self.scroll_bounds = {
            'min_x': self.screen_width - self.surface_width,
            'max_x': 0,
            'min_y': self.screen_height - self.surface_height,
            'max_y': 0
            }
        self.scroll_x = self.scroll_bounds['max_x']
        self.scroll_y = self.scroll_bounds['min_y']

    def _choose_building_for_event(self, x,y):
        for building, [x_0, x_1] in self.buildings_with_pos_x:
            if x_0 <= x <= x_1:
                if ((self.surface_height) - y) <= building.surface_height:
                    return building, x - x_0
        return None,None
            
    def go_live(self):
        clock = pygame.time.Clock()
        last_iteration = 0
        running = True
        while running:
            # track time laps and update global variable
            tick = pygame.time.get_ticks()
            global_vars.GAME_ITERATION_LAPS_TIME_MS = tick -last_iteration
            last_iteration = tick

            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        running = False

                    case pygame.MOUSEWHEEL:
                        self.scroll_x = max(min(self.scroll_x - event.x * global_vars.GAME_SCROLL_PX_PER_SWIPE, self.scroll_bounds['max_x']), self.scroll_bounds['min_x'])
                        self.scroll_y = max(min(self.scroll_y + event.y * global_vars.GAME_SCROLL_PX_PER_SWIPE, self.scroll_bounds['max_y']),self.scroll_bounds['min_y'])
                    
                    case pygame.MOUSEBUTTONUP:
                        # avoid events generated from scrolling
                        if event.button not in (4, 5):
                            x,y = pygame.mouse.get_pos()
                            x -= self.scroll_x
                            y -= self.scroll_y

                            relevant_building, adjusted_x = self._choose_building_for_event(x, y)
                            
                            if relevant_building is not None:
                                adjusted_y = relevant_building.surface_height - (self.surface_height - y)
                                relevant_building.handle_click_event(adjusted_x, adjusted_y)

            # Fill the background with white
            self.scrolable_surface.fill('white')
            for building, [x_0, x_1] in self.buildings_with_pos_x:
                building.update_and_draw()
                self.scrolable_surface.blit(building.surface, (x_0, self.surface_height - building.surface_height))
            
            self.screen.blit(self.scrolable_surface, (self.scroll_x, self.scroll_y))

            clock.tick(global_vars.GAME_MAX_ITERATIONS_PER_SECOND)
            # # Flip the display
            pygame.display.flip()
        # Done! Time to quit.
        pygame.quit()


building_complex = BuildingsSystem()
building_complex.go_live()
